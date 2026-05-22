# AEGIS Secure Backend

All database files are encrypted at rest with **AES-256-GCM** before being written to disk.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example ../.env
# Edit ../.env — set DATABASE_ENCRYPTION_KEY to a long random secret (32+ chars)
# Generate: openssl rand -base64 48

uvicorn main:app --host 127.0.0.1 --port 8000
```

Run everything from the project root:

```bash
npm run dev:all
```

Or separately: `uvicorn` here, `npm run dev` at repo root (Vite proxies `/api` and `/pmi` to port 8000), and `streamlit run streamlit_rag_dashboard.py` below.

## Encrypted stores

| Store      | File                         | Contents              |
|------------|------------------------------|-----------------------|
| autopsies  | `data/encrypted/autopsies.enc` | Forensic records    |
| evidence   | `data/encrypted/evidence.enc`  | Vector search index |
| timelines  | `data/encrypted/timelines.enc`   | Case timelines      |
| movement   | `data/encrypted/movement.enc`    | Movement traces     |

Check status: `GET /api/security/status` or **Settings** in the AEGIS UI.

## RAG dashboard (Streamlit)

Pipeline overview and demo search, separate from the React app:

```bash
cd backend
source .venv/bin/activate
pip install streamlit pandas
streamlit run streamlit_rag_dashboard.py
```

Opens at `http://localhost:8501`.

## Key rotation

1. Decrypt with the old key (export data via API).
2. Set a new `DATABASE_ENCRYPTION_KEY` in `.env`.
3. Delete `data/encrypted/*.enc` and restart (re-seeds) or call `POST /api/admin/reencrypt` after loading data.

Never commit `.env` or `data/encrypted/`.
