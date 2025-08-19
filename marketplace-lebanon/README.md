# Lebanese Student Marketplace

A minimal FastAPI app where students in Lebanon can buy/sell items (LBP/USD), filter by university, and message sellers.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`.

## Features
- Email+password signup/login (cookie-based)
- Create listings with image upload
- Search and filter by query, category, currency, university, price
- Message sellers; view inbox

## Notes
- Uses SQLite (`data.db`) in project root
- Update `SECRET_KEY` in `app/auth.py` for production