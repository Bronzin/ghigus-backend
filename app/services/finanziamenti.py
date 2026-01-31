# app/services/finanziamenti.py
"""Gestione nuovi finanziamenti con piano di ammortamento."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_finanziamento import MdmNuovoFinanziamento, MdmFinanziamentoSchedule

D = Decimal
ZERO = D(0)


def _compute_ammortamento_francese(capitale: D, tasso_annuo: D, durata_mesi: int) -> List[Dict]:
    """Ammortamento alla francese (rata costante)."""
    tasso_m = tasso_annuo / 12
    if tasso_m == ZERO:
        rata = (capitale / durata_mesi).quantize(D("0.01"))
        rows = []
        residuo = capitale
        for i in range(durata_mesi):
            q_interessi = ZERO
            q_capitale = rata if i < durata_mesi - 1 else residuo
            residuo -= q_capitale
            rows.append({
                "quota_capitale": q_capitale,
                "quota_interessi": q_interessi,
                "rata": q_capitale,
                "debito_residuo": max(residuo, ZERO),
            })
        return rows

    rata = (capitale * tasso_m / (1 - (1 + tasso_m) ** (-durata_mesi))).quantize(D("0.01"))
    rows = []
    residuo = capitale
    for i in range(durata_mesi):
        q_interessi = (residuo * tasso_m).quantize(D("0.01"))
        q_capitale = rata - q_interessi
        if i == durata_mesi - 1:
            q_capitale = residuo
            rata = q_capitale + q_interessi
        residuo -= q_capitale
        rows.append({
            "quota_capitale": q_capitale,
            "quota_interessi": q_interessi,
            "rata": rata,
            "debito_residuo": max(residuo, ZERO),
        })
    return rows


def _compute_ammortamento_italiano(capitale: D, tasso_annuo: D, durata_mesi: int) -> List[Dict]:
    """Ammortamento all'italiana (quota capitale costante)."""
    tasso_m = tasso_annuo / 12
    q_capitale = (capitale / durata_mesi).quantize(D("0.01"))
    rows = []
    residuo = capitale
    for i in range(durata_mesi):
        q_interessi = (residuo * tasso_m).quantize(D("0.01"))
        qc = q_capitale if i < durata_mesi - 1 else residuo
        rata = qc + q_interessi
        residuo -= qc
        rows.append({
            "quota_capitale": qc,
            "quota_interessi": q_interessi,
            "rata": rata,
            "debito_residuo": max(residuo, ZERO),
        })
    return rows


def _compute_ammortamento_bullet(capitale: D, tasso_annuo: D, durata_mesi: int) -> List[Dict]:
    """Bullet: solo interessi, rimborso capitale alla scadenza."""
    tasso_m = tasso_annuo / 12
    rows = []
    for i in range(durata_mesi):
        q_interessi = (capitale * tasso_m).quantize(D("0.01"))
        q_capitale = capitale if i == durata_mesi - 1 else ZERO
        residuo = ZERO if i == durata_mesi - 1 else capitale
        rows.append({
            "quota_capitale": q_capitale,
            "quota_interessi": q_interessi,
            "rata": q_capitale + q_interessi,
            "debito_residuo": residuo,
        })
    return rows


def compute_finanziamento_schedule(fin: MdmNuovoFinanziamento) -> List[Dict]:
    """Calcola il piano di ammortamento per un finanziamento."""
    # Per finanziamenti esistenti: usa debito_residuo_iniziale e rate_rimanenti
    if fin.is_existing:
        capitale = fin.debito_residuo_iniziale or ZERO
        durata = fin.rate_rimanenti or fin.durata_mesi or 60
    else:
        capitale = fin.importo_capitale or ZERO
        durata = fin.durata_mesi or 60

    tasso = (fin.tasso_annuo or ZERO) / 100

    if capitale <= ZERO or durata <= 0:
        return []

    tipo = (fin.tipo_ammortamento or "FRANCESE").upper()
    if tipo == "ITALIANO":
        return _compute_ammortamento_italiano(capitale, tasso, durata)
    elif tipo == "BULLET":
        return _compute_ammortamento_bullet(capitale, tasso, durata)
    else:
        return _compute_ammortamento_francese(capitale, tasso, durata)


def save_finanziamento_schedule(db: Session, fin: MdmNuovoFinanziamento) -> int:
    """Calcola e salva il piano di ammortamento per un finanziamento."""
    db.query(MdmFinanziamentoSchedule).filter(
        MdmFinanziamentoSchedule.finanziamento_id == fin.id
    ).delete()

    rows = compute_finanziamento_schedule(fin)
    mese_erog = fin.mese_erogazione or 0

    for i, row in enumerate(rows):
        db.add(MdmFinanziamentoSchedule(
            finanziamento_id=fin.id,
            period_index=mese_erog + i,
            quota_capitale=row["quota_capitale"],
            quota_interessi=row["quota_interessi"],
            rata=row["rata"],
            debito_residuo=row["debito_residuo"],
        ))

    db.commit()
    return len(rows)


def get_finanziamenti(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmNuovoFinanziamento]:
    return (
        db.query(MdmNuovoFinanziamento)
        .filter(MdmNuovoFinanziamento.case_id == case_id,
                MdmNuovoFinanziamento.scenario_id == scenario_id)
        .order_by(MdmNuovoFinanziamento.mese_erogazione, MdmNuovoFinanziamento.id)
        .all()
    )


def get_finanziamento_schedule(db: Session, fin_id: int) -> List[MdmFinanziamentoSchedule]:
    return (
        db.query(MdmFinanziamentoSchedule)
        .filter(MdmFinanziamentoSchedule.finanziamento_id == fin_id)
        .order_by(MdmFinanziamentoSchedule.period_index)
        .all()
    )


def get_all_finanziamenti_by_period(db: Session, case_id: str, scenario_id: str = "base") -> Dict[int, Dict[str, D]]:
    """
    Aggrega tutti i finanziamenti per period_index.
    Ritorna {period_index: {erogazione, quota_capitale, quota_interessi, rata, debito_residuo_totale}}.
    """
    fins = get_finanziamenti(db, case_id, scenario_id)
    if not fins:
        return {}

    by_period: Dict[int, Dict[str, D]] = {}

    for fin in fins:
        mese_erog = fin.mese_erogazione or 0
        schedules = get_finanziamento_schedule(db, fin.id)

        # Erogazione: solo per nuovi finanziamenti (non existing)
        if not fin.is_existing:
            if mese_erog not in by_period:
                by_period[mese_erog] = {"erogazione": ZERO, "quota_capitale": ZERO,
                                         "quota_interessi": ZERO, "rata": ZERO}
            by_period[mese_erog]["erogazione"] += fin.importo_capitale or ZERO

        for s in schedules:
            pi = s.period_index
            if pi not in by_period:
                by_period[pi] = {"erogazione": ZERO, "quota_capitale": ZERO,
                                  "quota_interessi": ZERO, "rata": ZERO}
            by_period[pi]["quota_capitale"] += s.quota_capitale or ZERO
            by_period[pi]["quota_interessi"] += s.quota_interessi or ZERO
            by_period[pi]["rata"] += s.rata or ZERO

    return by_period


def create_finanziamento(db: Session, case_id: str, scenario_id: str, data: dict) -> MdmNuovoFinanziamento:
    """Crea un nuovo finanziamento e calcola il piano."""
    is_existing = data.get("is_existing", False)
    fin = MdmNuovoFinanziamento(
        case_id=case_id,
        scenario_id=scenario_id,
        label=data["label"],
        importo_capitale=D(str(data["importo_capitale"])),
        tasso_annuo=D(str(data.get("tasso_annuo", 3.0))),
        durata_mesi=data.get("durata_mesi", 60),
        mese_erogazione=data.get("mese_erogazione", 0),
        tipo_ammortamento=data.get("tipo_ammortamento", "FRANCESE"),
        is_existing=is_existing,
        debito_residuo_iniziale=D(str(data["debito_residuo_iniziale"])) if data.get("debito_residuo_iniziale") is not None else None,
        rate_rimanenti=data.get("rate_rimanenti"),
    )
    db.add(fin)
    db.flush()
    save_finanziamento_schedule(db, fin)
    return fin


def delete_finanziamento(db: Session, fin_id: int) -> bool:
    """Elimina un finanziamento (cascade elimina lo schedule)."""
    fin = db.query(MdmNuovoFinanziamento).filter(MdmNuovoFinanziamento.id == fin_id).first()
    if not fin:
        return False
    db.delete(fin)
    db.commit()
    return True
