# app/db/base.py
from app.db.base_class import Base  # noqa: F401

# Importa i modelli in modo che Base.metadata li registri
from app.db.models.case import Case  # noqa: F401
from app.db.models.staging import TBEntry, XbrlFact, MapSP, MapCE  # noqa: F401
from app.db.models.final import SpRiclass, CeRiclass, KpiStandard  # noqa: F401

# MDM models
from app.db.models.mdm_attivo import MdmAttivoItem  # noqa: F401
from app.db.models.mdm_passivo import MdmPassivoItem, MdmPassivoTipologia  # noqa: F401
from app.db.models.mdm_liquidazione import MdmLiquidazione, MdmTestPiat  # noqa: F401
from app.db.models.mdm_prededuzione import MdmPrededuzioneMonthly  # noqa: F401
from app.db.models.mdm_affitto import MdmAffittoMonthly  # noqa: F401
from app.db.models.mdm_cessione import MdmCessioneMonthly  # noqa: F401
from app.db.models.mdm_projections import (  # noqa: F401
    MdmCeProjection, MdmSpProjection,
    MdmCflowProjection, MdmBancaProjection,
)
from app.db.models.mdm_concordato import MdmConcordatoMonthly  # noqa: F401
from app.db.models.mdm_scenario import MdmScenario  # noqa: F401
from app.db.models.mdm_attivo_schedule import MdmAttivoSchedule  # noqa: F401
from app.db.models.mdm_finanziamento import MdmNuovoFinanziamento, MdmFinanziamentoSchedule  # noqa: F401
