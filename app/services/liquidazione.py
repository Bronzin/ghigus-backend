# app/services/liquidazione.py
"""
Waterfall di liquidazione giudiziale con distribuzione per masse.

Concetto di "masse" nel diritto fallimentare italiano:
  Massa 1 (Immobiliare): realizzo da immobili → ipotecari hanno prelazione
  Massa 2 (Mobiliare): realizzo da beni mobili, crediti, rimanenze
  Massa 3 (Generale): disponibilità liquide, cassa

Waterfall di distribuzione:
  1. Calcolo realizzo per massa (attivo rettificato raggruppato per categoria)
  2. Deduzione spese di liquidazione (% configurabile)
  3. Prededuzioni: distribuite pro-rata su tutte le masse
  4. Ipotecari: soddisfatti dalla massa 1 (immobiliare)
  5. Privilegiati: soddisfatti dalla massa 2 (mobiliare) + residuo massa 1
  6. Chirografari: soddisfatti dal residuo di tutte le masse

Output: righe dettagliate con importo_totale e importo_massa_1/2/3 per ogni classe.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_liquidazione import MdmLiquidazione
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_passivo import MdmPassivoItem
from app.services.assumptions import get_assumptions_or_default

D = Decimal
ZERO = D(0)


def _sum_attivo_by_massa(
    attivo_items: List[MdmAttivoItem],
    categorie_m1: List[str],
    categorie_m2: List[str],
    categorie_m3: List[str],
) -> tuple:
    """Raggruppa il realizzo attivo rettificato per massa."""
    massa_1 = ZERO
    massa_2 = ZERO
    massa_3 = ZERO
    for item in attivo_items:
        val = item.attivo_rettificato or ZERO
        cat = item.category
        if cat in categorie_m1:
            massa_1 += val
        elif cat in categorie_m3:
            massa_3 += val
        elif cat in categorie_m2:
            massa_2 += val
        else:
            # Default: massa mobiliare
            massa_2 += val
    return massa_1, massa_2, massa_3


def _distribute_prorata(amount: D, m1: D, m2: D, m3: D) -> tuple:
    """Distribuisce un importo pro-rata sulle masse in base ai loro valori."""
    total = m1 + m2 + m3
    if total == ZERO:
        return ZERO, ZERO, ZERO
    d1 = (amount * m1 / total).quantize(D("0.01"))
    d2 = (amount * m2 / total).quantize(D("0.01"))
    d3 = amount - d1 - d2  # residuo per evitare errori di arrotondamento
    return d1, d2, d3


def _pay_from_masse(credito: D, disponibile_m1: D, disponibile_m2: D, disponibile_m3: D,
                     priority: str) -> tuple:
    """
    Paga un credito dalle masse secondo la priorità:
      IPOTECARIO: massa 1 → massa 3 → massa 2
      PRIVILEGIATO: massa 2 → massa 1 → massa 3
      CHIROGRAFARIO: massa 3 → massa 2 → massa 1
    Restituisce (pagato_m1, pagato_m2, pagato_m3, residuo_credito,
                 nuovo_disp_m1, nuovo_disp_m2, nuovo_disp_m3)
    """
    if priority == "IPOTECARIO":
        order = [1, 3, 2]
    elif priority == "PRIVILEGIATO":
        order = [2, 1, 3]
    else:  # CHIROGRAFARIO o altro
        order = [3, 2, 1]

    disponibile = {1: disponibile_m1, 2: disponibile_m2, 3: disponibile_m3}
    pagato = {1: ZERO, 2: ZERO, 3: ZERO}
    remaining = credito

    for m in order:
        if remaining <= ZERO:
            break
        pay = min(remaining, disponibile[m])
        pagato[m] = pay
        disponibile[m] -= pay
        remaining -= pay

    return (pagato[1], pagato[2], pagato[3], remaining,
            disponibile[1], disponibile[2], disponibile[3])


def compute_liquidazione(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Calcola la waterfall di liquidazione giudiziale con 3 masse.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmLiquidazione).filter(
        MdmLiquidazione.case_id == case_id,
        MdmLiquidazione.scenario_id == scenario_id,
    ).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    liq_params = assumptions.liquidazione
    pct_spese = D(str(liq_params.pct_spese_liquidazione)) / 100

    # ── 1. Realizzo attivo per massa ──
    attivo_items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()

    m1_lordo, m2_lordo, m3_lordo = _sum_attivo_by_massa(
        attivo_items,
        liq_params.categorie_massa_1,
        liq_params.categorie_massa_2,
        liq_params.categorie_massa_3,
    )
    realizzo_lordo = m1_lordo + m2_lordo + m3_lordo

    count = 0

    # Riga: Realizzo lordo per massa
    db.add(MdmLiquidazione(
        case_id=case_id, scenario_id=scenario_id,
        section="REALIZZO_ATTIVO", line_code="REALIZZO_LORDO",
        line_label="Realizzo lordo attivo",
        importo_totale=realizzo_lordo,
        importo_massa_1=m1_lordo, importo_massa_2=m2_lordo, importo_massa_3=m3_lordo,
    ))
    count += 1

    # ── 2. Spese di liquidazione ──
    spese_m1 = (m1_lordo * pct_spese).quantize(D("0.01"))
    spese_m2 = (m2_lordo * pct_spese).quantize(D("0.01"))
    spese_m3 = (m3_lordo * pct_spese).quantize(D("0.01"))
    spese_totali = spese_m1 + spese_m2 + spese_m3

    db.add(MdmLiquidazione(
        case_id=case_id, scenario_id=scenario_id,
        section="REALIZZO_ATTIVO", line_code="SPESE_LIQUIDAZIONE",
        line_label=f"Spese di liquidazione ({liq_params.pct_spese_liquidazione}%)",
        importo_totale=-spese_totali,
        importo_massa_1=-spese_m1, importo_massa_2=-spese_m2, importo_massa_3=-spese_m3,
    ))
    count += 1

    # Realizzo netto per massa
    disp_m1 = m1_lordo - spese_m1
    disp_m2 = m2_lordo - spese_m2
    disp_m3 = m3_lordo - spese_m3
    realizzo_netto = disp_m1 + disp_m2 + disp_m3

    db.add(MdmLiquidazione(
        case_id=case_id, scenario_id=scenario_id,
        section="REALIZZO_ATTIVO", line_code="REALIZZO_NETTO",
        line_label="Realizzo netto attivo",
        importo_totale=realizzo_netto,
        importo_massa_1=disp_m1, importo_massa_2=disp_m2, importo_massa_3=disp_m3,
    ))
    count += 1

    # ── 3. Recupera passivo per tipologia_creditore ──
    passivo_items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
        MdmPassivoItem.category != "PATRIMONIO_NETTO",
    ).all()

    by_tipo: Dict[str, D] = {}
    for item in passivo_items:
        tipo = item.tipologia_creditore or "CHIROGRAFARIO"
        by_tipo[tipo] = by_tipo.get(tipo, ZERO) + abs(item.passivo_rettificato or ZERO)

    # ── 4. Waterfall per classe di credito ──
    priority_order = [
        ("PREDEDUZIONE", "PREDEDUZIONI", "Crediti in prededuzione"),
        ("IPOTECARIO", "IPOTECARI", "Creditori ipotecari"),
        ("PRIVILEGIATO", "PRIVILEGIATI", "Creditori privilegiati"),
        ("CHIROGRAFARIO", "CHIROGRAFARI", "Creditori chirografari"),
    ]

    for tipo, section, label in priority_order:
        credito = by_tipo.get(tipo, ZERO)

        if tipo == "PREDEDUZIONE":
            # Prededuzioni: distribuite pro-rata su tutte le masse
            if credito > ZERO:
                p1, p2, p3 = _distribute_prorata(min(credito, realizzo_netto), disp_m1, disp_m2, disp_m3)
                pagato = p1 + p2 + p3
                disp_m1 -= p1
                disp_m2 -= p2
                disp_m3 -= p3
            else:
                p1, p2, p3 = ZERO, ZERO, ZERO
                pagato = ZERO
        else:
            # Ipotecari/Privilegiati/Chirografari: pagati secondo priorità massa
            p1, p2, p3, residuo, disp_m1, disp_m2, disp_m3 = _pay_from_masse(
                credito, disp_m1, disp_m2, disp_m3, tipo
            )
            pagato = p1 + p2 + p3

        residuo_credito = credito - pagato
        pct = (pagato / credito * 100).quantize(D("0.01")) if credito > ZERO else ZERO

        # Riga credito totale per questa classe
        db.add(MdmLiquidazione(
            case_id=case_id, scenario_id=scenario_id,
            section=section,
            line_code=f"CREDITO_{tipo}",
            line_label=f"{label} - credito ammesso",
            importo_totale=credito,
        ))
        count += 1

        # Riga distribuzione per massa
        db.add(MdmLiquidazione(
            case_id=case_id, scenario_id=scenario_id,
            section=section,
            line_code=f"DISTRIBUZIONE_{tipo}",
            line_label=f"{label} - distribuzione",
            importo_totale=pagato,
            importo_massa_1=p1, importo_massa_2=p2, importo_massa_3=p3,
            pct_soddisfazione=pct,
            credito_residuo=residuo_credito,
        ))
        count += 1

    # ── 5. Riepilogo disponibilità residua ──
    residuo_totale = disp_m1 + disp_m2 + disp_m3
    db.add(MdmLiquidazione(
        case_id=case_id, scenario_id=scenario_id,
        section="RIEPILOGO", line_code="DISPONIBILITA_RESIDUA",
        line_label="Disponibilità residua dopo distribuzione",
        importo_totale=residuo_totale,
        importo_massa_1=disp_m1, importo_massa_2=disp_m2, importo_massa_3=disp_m3,
    ))
    count += 1

    # Riepilogo % soddisfazione per classe
    for tipo, section, label in priority_order:
        credito = by_tipo.get(tipo, ZERO)
        # Recupera la riga distribuzione appena inserita per leggere pagato
        dist_row = (
            db.query(MdmLiquidazione)
            .filter(
                MdmLiquidazione.case_id == case_id,
                MdmLiquidazione.scenario_id == scenario_id,
                MdmLiquidazione.line_code == f"DISTRIBUZIONE_{tipo}",
            )
            .first()
        )
        pagato = (dist_row.importo_totale or ZERO) if dist_row else ZERO
        pct = (pagato / credito * 100).quantize(D("0.01")) if credito > ZERO else ZERO

        db.add(MdmLiquidazione(
            case_id=case_id, scenario_id=scenario_id,
            section="RIEPILOGO",
            line_code=f"SODDISFAZIONE_{tipo}",
            line_label=f"% soddisfazione {label.lower()}",
            importo_totale=credito,
            pct_soddisfazione=pct,
            credito_residuo=credito - pagato,
        ))
        count += 1

    db.commit()
    return count


def get_liquidazione(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmLiquidazione]:
    return (
        db.query(MdmLiquidazione)
        .filter(
            MdmLiquidazione.case_id == case_id,
            MdmLiquidazione.scenario_id == scenario_id,
        )
        .order_by(MdmLiquidazione.id)
        .all()
    )
