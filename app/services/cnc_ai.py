# app/services/cnc_ai.py
"""
Generatore di commenti AI per analisi finanziarie CNC

Genera commenti professionali per le tabelle finanziarie usando OpenAI API.
Include modalità mock per test senza costi API.
Usa PromptBuilder per prompt professionali strutturati.

Ported from ghigus-cnc/src/ai_generator.py.
"""
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from app.services.cnc_prompts import PromptBuilder

logger = logging.getLogger(__name__)

# Istanza globale del prompt builder
_prompt_builder = PromptBuilder()


@dataclass
class AIResponse:
    """Risposta del generatore AI"""
    content: str
    prompt_type: str
    is_mock: bool
    tokens_used: int = 0


def _extract_periodo(table_data: list[list[str]]) -> str:
    """
    Estrae il periodo dai dati della tabella cercando la riga con gli anni.

    Gestisce:
    - Anni semplici: "2021", "2025"
    - Anni con separatore migliaia italiano: "2.021", "2.025"
    - Header "Anno 1", "Anno 2" style
    """
    for row in table_data[:10]:
        years_found: list[str] = []
        for cell in row:
            cell_str = str(cell).strip()
            if not cell_str:
                continue
            # Pattern 1: anno semplice "2024"
            match = re.fullmatch(r"(20\d{2})", cell_str)
            if match:
                years_found.append(match.group(1))
                continue
            # Pattern 2: anno con separatore migliaia "2.024"
            match = re.fullmatch(r"2\.0(\d{2})", cell_str)
            if match:
                years_found.append(f"20{match.group(1)}")
                continue

        if len(years_found) >= 2:
            seen: list[str] = []
            for y in years_found:
                if y not in seen:
                    seen.append(y)
            return f"{seen[0]}-{seen[-1]}"
        elif len(years_found) == 1:
            return years_found[0]

    return "periodo analizzato"


def _generate_mock_comment(prompt_type: str, table_data: list[list[str]]) -> str:
    """Genera un commento mock per test senza API"""
    year_range = _extract_periodo(table_data)

    mock_comments = {
        "analisi_economica": f"""L'analisi del Conto Economico per il periodo {year_range} evidenzia un andamento
caratterizzato da significative variazioni nei principali aggregati economici. Il valore della produzione
mostra un trend che richiede attenzione, con margini operativi che hanno subito pressioni nel corso
degli esercizi analizzati.

Il Margine Operativo Lordo (MOL) presenta oscillazioni che riflettono sia la dinamica dei ricavi
sia l'evoluzione della struttura dei costi. L'incidenza dei costi fissi sul fatturato rappresenta
un elemento critico da monitorare nell'ambito del piano di risanamento.

Il risultato netto evidenzia la necessità di interventi strutturali per ripristinare condizioni
di equilibrio economico sostenibile nel medio-lungo periodo.""",

        "analisi_finanziaria": f"""Il Rendiconto Finanziario per il periodo {year_range} mostra una dinamica
dei flussi di cassa che richiede particolare attenzione. I flussi operativi presentano variazioni
significative, influenzati dalla gestione del capitale circolante e dall'andamento economico.

La gestione degli investimenti ha assorbito risorse finanziarie, mentre l'attività di finanziamento
mostra un ricorso crescente a fonti esterne. La posizione di cassa finale riflette le tensioni
finanziarie che hanno caratterizzato il periodo.

La capacità di generazione di cassa operativa rappresenta un elemento chiave da rafforzare
nel contesto del piano di ristrutturazione proposto.""",

        "stato_patrimoniale": f"""L'analisi dello Stato Patrimoniale per il periodo {year_range} evidenzia
una struttura patrimoniale che ha subito significative modifiche. L'attivo mostra una composizione
che riflette le scelte strategiche dell'azienda, con particolare riferimento alla gestione
del capitale circolante e degli investimenti.

Sul fronte del passivo, si rileva un'evoluzione del rapporto tra mezzi propri e mezzi di terzi
che richiede attenzione. Il patrimonio netto ha registrato variazioni correlate ai risultati
economici conseguiti negli esercizi analizzati.

Gli indici di solidità patrimoniale suggeriscono la necessità di interventi volti al
riequilibrio della struttura finanziaria complessiva.""",

        "posizione_finanziaria_netta": f"""La Posizione Finanziaria Netta (PFN) nel periodo {year_range}
mostra un'evoluzione che riflette le dinamiche finanziarie dell'azienda. Il livello di
indebitamento finanziario netto ha subito variazioni correlate sia alla gestione operativa
sia alle scelte di investimento.

Il rapporto PFN/MOL evidenzia un livello di leva finanziaria che richiede monitoraggio
nel contesto del piano di risanamento. La composizione del debito tra breve e lungo termine
influenza la gestione della liquidità aziendale.

La sostenibilità dell'indebitamento rappresenta un elemento centrale nella valutazione
della fattibilità del piano proposto.""",

        "rettifiche_attivo": f"""Le rettifiche applicate all'Attivo Patrimoniale evidenziano un processo
di valutazione prudenziale delle poste attive. L'analisi ha interessato le principali categorie
di immobilizzazioni e di attivo circolante, con l'obiettivo di determinare i valori di realizzo
effettivi nel contesto della procedura.

Le svalutazioni applicate riflettono le condizioni di mercato e la possibilità concreta
di recupero dei valori iscritti in bilancio. Il totale delle rettifiche determina l'attivo
rettificato disponibile per il soddisfacimento dei creditori.""",

        "rettifiche_passivo": f"""Le rettifiche al Passivo Patrimoniale riflettono la riclassificazione
dei debiti per categoria di creditore e l'applicazione delle percentuali di soddisfacimento
previste dal piano. L'analisi ha interessato tutte le classi di creditori, distinguendo
tra privilegiati e chirografari.

Il trattamento proposto tiene conto della gerarchia delle cause di prelazione e della
disponibilità patrimoniale risultante dalle rettifiche all'attivo. Le percentuali di
soddisfacimento sono state determinate in coerenza con i flussi finanziari previsti.""",

        "piano_flussi": f"""Il Piano dei Flussi Finanziari per il periodo {year_range} presenta la dinamica
di tesoreria prevista mese per mese. Le entrate operative derivano principalmente dall'attività
caratteristica dell'azienda, integrate da eventuali realizzi di asset.

Le uscite comprendono i costi operativi correnti, le spese prededucibili della procedura
e i pagamenti ai creditori concordatari secondo il calendario previsto. Il saldo progressivo
dimostra la sostenibilità finanziaria del piano proposto.""",

        "piano_creditori": f"""Il Piano di Soddisfacimento Creditori per il periodo {year_range} dettaglia
le modalità e le tempistiche di pagamento per ciascuna categoria di creditore. I creditori
prededucibili sono soddisfatti con priorità, seguiti dai privilegiati e dai chirografari.

Le percentuali di soddisfacimento proposte risultano superiori a quelle ottenibili in caso
di liquidazione giudiziale, dimostrando la convenienza del piano per tutte le classi
di creditori interessate.""",

        "conclusioni": """Il Piano di Ristrutturazione dei Debiti proposto si basa su un'analisi
approfondita della situazione aziendale e prospetta un percorso di risanamento credibile.

L'analisi economico-finanziaria ha evidenziato le cause della crisi e identificato le
leve di intervento necessarie. Il piano prevede azioni concrete per il ripristino
dell'equilibrio economico e finanziario.

I creditori potranno beneficiare di percentuali di soddisfacimento superiori rispetto
all'alternativa liquidatoria, con tempistiche definite e coerenti con la capacità
di generazione di cassa prevista.

Si ritiene che il piano presenti i requisiti di fattibilità e convenienza necessari
per l'omologazione da parte del Tribunale.""",
    }

    return mock_comments.get(prompt_type, mock_comments["stato_patrimoniale"])


def _call_openai_api(system_prompt: str, user_prompt: str) -> tuple[str, int]:
    """Chiama l'API OpenAI e ritorna (risposta, tokens_usati)"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Modulo openai non installato. Esegui: pip install openai")

    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY non configurata")

    if api_key == "sk-your-key-here":
        raise ValueError(
            "OPENAI_API_KEY contiene ancora il placeholder. Configura la tua API key in .env"
        )

    client = OpenAI(api_key=api_key)

    logger.info("Chiamata API OpenAI (model: %s)...", model)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1200,
    )

    content = response.choices[0].message.content or ""
    tokens = response.usage.total_tokens if response.usage else 0

    logger.info("Risposta ricevuta (%d tokens)", tokens)

    return content, tokens


def generate_comment(
    table_data: list[list[str]],
    prompt_type: str,
    use_mock: Optional[bool] = None,
    periodo: Optional[str] = None,
    anno: Optional[int] = None,
    anno_riferimento: Optional[str] = None,
    dati_sintesi: Optional[dict[str, str]] = None,
) -> AIResponse:
    """
    Genera un commento AI per una tabella finanziaria.

    Args:
        table_data: Lista di righe, ogni riga è una lista di valori stringa
        prompt_type: Tipo di analisi (es. "analisi_economica", "stato_patrimoniale")
        use_mock: Se True usa mock, se False usa API. None usa env USE_MOCK.
        periodo: Periodo di analisi (es. "2021-2025"). Se None, estratto dalla tabella.
        anno: Anno specifico per piano_flussi e piano_creditori
        anno_riferimento: Anno riferimento per rettifiche
        dati_sintesi: Dati di sintesi per conclusioni

    Returns:
        AIResponse con il commento generato
    """
    if use_mock is None:
        use_mock = os.environ.get("CNC_USE_MOCK", "true").lower() in ("true", "1", "yes")

    if use_mock:
        logger.info("Usando mock per: %s", prompt_type)
        content = _generate_mock_comment(prompt_type, table_data)
        return AIResponse(
            content=content,
            prompt_type=prompt_type,
            is_mock=True,
            tokens_used=0,
        )

    logger.info("Chiamata OpenAI per: %s", prompt_type)

    # Costruisci prompt professionale tramite PromptBuilder
    if periodo is None:
        periodo = _extract_periodo(table_data)

    try:
        if prompt_type == "conclusioni":
            prompts = _prompt_builder.conclusioni(dati_sintesi or {})
        elif prompt_type in ("piano_flussi", "piano_creditori"):
            _anno = anno or 1
            prompts = _prompt_builder.get_prompt(
                prompt_type, table_data=table_data, anno=_anno
            )
        elif prompt_type in ("rettifiche_attivo", "rettifiche_passivo"):
            prompts = _prompt_builder.get_prompt(
                prompt_type,
                table_data=table_data,
                anno_riferimento=anno_riferimento or "",
            )
        else:
            prompts = _prompt_builder.get_prompt(
                prompt_type, table_data=table_data, periodo=periodo
            )
    except ValueError:
        # Fallback: tipo non supportato, usa analisi generica
        logger.warning(
            "Tipo '%s' non in PromptBuilder, uso stato_patrimoniale", prompt_type
        )
        prompts = _prompt_builder.stato_patrimoniale(table_data, periodo)

    content, tokens = _call_openai_api(prompts["system"], prompts["user"])
    return AIResponse(
        content=content,
        prompt_type=prompt_type,
        is_mock=False,
        tokens_used=tokens,
    )


def list_prompt_types() -> list[str]:
    """Ritorna l'elenco dei tipi di prompt disponibili"""
    return [
        "analisi_economica",
        "analisi_finanziaria",
        "stato_patrimoniale",
        "posizione_finanziaria_netta",
        "rettifiche_attivo",
        "rettifiche_passivo",
        "piano_flussi",
        "piano_creditori",
        "conclusioni",
    ]
