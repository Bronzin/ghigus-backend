# app/db/base.py
from app.db.base_class import Base  # noqa: F401

# Importa i modelli in modo che Base.metadata li registri
from app.db.models.case import Case  # noqa: F401
from app.db.models.staging import TBEntry, XbrlFact, MapSP, MapCE  # noqa: F401
from app.db.models.final import SpRiclass, CeRiclass, KpiStandard  # noqa: F401
