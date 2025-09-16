# ghigus-backend

Backend FastAPI per Ghigus con endpoint mock per la gestione delle pratiche.

## Requisiti

- Python 3.11+
- [Poetry](https://python-poetry.org/) o `pip` classico per installare le dipendenze elencate in `requirements.txt`
- Database PostgreSQL (per ambiente locale è sufficiente anche SQLite modificando `DATABASE_URL`)

## Configurazione

1. Copia il file `.env.example` e rinominalo `.env`, aggiornando i valori per il tuo ambiente:
   ```bash
   cp .env.example .env
   ```
2. Installa le dipendenze applicative:
   ```bash
   pip install -r requirements.txt
   ```

## Avviare il server in locale

Esegui il server FastAPI utilizzando Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 10000
```

Il servizio sarà raggiungibile su `http://localhost:10000` e l'endpoint di health check risponderà su `/health`.

## Migrazioni database

Questo progetto utilizza Alembic per le migrazioni. Per applicare le migrazioni esistenti:

```bash
alembic upgrade head
```

Per generare una nuova migrazione dopo aver modificato il modello dati:

```bash
alembic revision --autogenerate -m "descrizione"
alembic upgrade head
```

Assicurati che la variabile di ambiente `DATABASE_URL` sia configurata correttamente prima di eseguire i comandi.

## Docker

È disponibile un `Dockerfile` minimale. Costruisci e avvia il container con:

```bash
docker build -t ghigus-backend .
docker run -p 10000:10000 --env-file .env ghigus-backend
```
