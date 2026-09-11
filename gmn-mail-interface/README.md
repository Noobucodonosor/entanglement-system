# GMN Mail Interface

Interfaccia web per parsing email e calcolo automatico di punteggi e acconti.

## Struttura

```
gmn-mail-interface/
├── backend/    # API FastAPI (parsing email, score, acconti)
└── frontend/   # Dashboard React
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponibile su `http://localhost:8000`. Docs interattive su `/docs`.

## Frontend

```bash
cd frontend
npm install
npm start
```

Dashboard su `http://localhost:3000`, con proxy verso il backend.

## Endpoint principali

- `GET  /api/emails` — elenco email processate
- `GET  /api/emails/{id}` — dettaglio singola email
- `POST /api/emails/upload` — upload file `.eml`, restituisce punteggio e acconto stimato
