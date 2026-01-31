# app/services/scadenziario_tributario.py
"""Gestione scadenziari debiti tributari (AdE / INPS) con piano rate."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_scadenziario_tributario import (
    MdmScadenziarioTributario,
    MdmScadenziarioTributarioRate,
)

D = Decimal
ZERO = D(0)


def _genera_rate(
    debito_originario: D,
    num_rate: int,
    tasso_annuo: D,
    sanzioni_totali: D,
    mese_inizio: int,
) -> List[Dict]:
    """
    Ammortamento italiano (quota capitale costante) + interessi su residuo + sanzioni pro-rata.
    """
    if debito_originario <= ZERO or num_rate <= 0:
        return []

    tasso_m = tasso_annuo / 100 / 12
    q_capitale = (debito_originario / num_rate).quantize(D("0.01"))
    q_sanzioni = (sanzioni_totali / num_rate).quantize(D("0.01"))

    rows = []
    residuo = debito_originario

    for i in range(num_rate):
        q_interessi = (residuo * tasso_m).quantize(D("0.01"))

        # Ultima rata: aggiusta per arrotondamento
        if i == num_rate - 1:
            qc = residuo
            qs = sanzioni_totali - q_sanzioni * (num_rate - 1)
        else:
            qc = q_capitale
            qs = q_sanzioni

        importo_rata = qc + q_interessi + qs
        residuo -= qc

        rows.append({
            "period_index": mese_inizio + i,
            "quota_capitale": qc,
            "quota_interessi": q_interessi,
            "quota_sanzioni": qs,
            "importo_rata": importo_rata,
            "debito_residuo": max(residuo, ZERO),
        })

    return rows


def create_scadenziario(db: Session, case_id: str, scenario_id: str, data: dict) -> MdmScadenziarioTributario:
    """Crea header scadenziario + genera rate."""
    sched = MdmScadenziarioTributario(
        case_id=case_id,
        scenario_id=scenario_id,
        ente=data["ente"],
        descrizione=data.get("descrizione"),
        debito_originario=D(str(data.get("debito_originario", 0))),
        num_rate=data.get("num_rate", 12),
        tasso_interessi=D(str(data.get("tasso_interessi", 0))),
        sanzioni_totali=D(str(data.get("sanzioni_totali", 0))),
        mese_inizio=data.get("mese_inizio", 0),
    )
    db.add(sched)
    db.flush()

    rows = _genera_rate(
        debito_originario=sched.debito_originario or ZERO,
        num_rate=sched.num_rate or 12,
        tasso_annuo=sched.tasso_interessi or ZERO,
        sanzioni_totali=sched.sanzioni_totali or ZERO,
        mese_inizio=sched.mese_inizio or 0,
    )

    for row in rows:
        db.add(MdmScadenziarioTributarioRate(
            scadenziario_id=sched.id,
            **row,
        ))

    db.commit()
    return sched


def get_scadenziari(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmScadenziarioTributario]:
    return (
        db.query(MdmScadenziarioTributario)
        .filter(
            MdmScadenziarioTributario.case_id == case_id,
            MdmScadenziarioTributario.scenario_id == scenario_id,
        )
        .order_by(MdmScadenziarioTributario.mese_inizio, MdmScadenziarioTributario.id)
        .all()
    )


def get_scadenziario_detail(db: Session, scadenziario_id: int):
    """Ritorna header + rate."""
    sched = db.query(MdmScadenziarioTributario).filter(
        MdmScadenziarioTributario.id == scadenziario_id
    ).first()
    if not sched:
        return None, []
    rate = (
        db.query(MdmScadenziarioTributarioRate)
        .filter(MdmScadenziarioTributarioRate.scadenziario_id == scadenziario_id)
        .order_by(MdmScadenziarioTributarioRate.period_index)
        .all()
    )
    return sched, rate


def delete_scadenziario(db: Session, scadenziario_id: int) -> bool:
    sched = db.query(MdmScadenziarioTributario).filter(
        MdmScadenziarioTributario.id == scadenziario_id
    ).first()
    if not sched:
        return False
    db.delete(sched)
    db.commit()
    return True


def get_tributari_by_period(db: Session, case_id: str, scenario_id: str = "base") -> Dict[int, D]:
    """
    Aggrega importo_rata per period_index su tutti gli scadenziari del caso.
    Ritorna {period_index: importo_rata_totale}.
    """
    scheds = get_scadenziari(db, case_id, scenario_id)
    if not scheds:
        return {}

    by_period: Dict[int, D] = {}
    for s in scheds:
        rate = (
            db.query(MdmScadenziarioTributarioRate)
            .filter(MdmScadenziarioTributarioRate.scadenziario_id == s.id)
            .all()
        )
        for r in rate:
            pi = r.period_index
            by_period[pi] = by_period.get(pi, ZERO) + (r.importo_rata or ZERO)

    return by_period
