# NewSolProduct — Solar Permit Plan Checker

An AI-assisted tool that parses solar permit PDFs and checks them against NEC 690/705 and common solar code requirements.

## Project Structure

```
NewSolProduct/
├── backend/
│   ├── main.py          # FastAPI app (API endpoints)
│   ├── extractor.py     # PDF text extraction (PyMuPDF)
│   ├── rules.py         # Rule engine (NEC 690/705 checks)
│   └── requirements.txt
└── frontend/
    └── index.html       # Upload UI + compliance report
```

## Getting Started

### 1. Run the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will start at `http://localhost:8000`

### 2. Open the Frontend

Open `frontend/index.html` directly in your browser.

Upload a solar permit PDF and click **Run Compliance Check**.

---

## What It Checks

| Rule | Reference |
|------|-----------|
| System size consistency (modules × wattage = stated kW) | General |
| Conductor sizing | NEC 690.8 |
| Rapid shutdown referenced | NEC 690.12 |
| DC disconnect referenced | NEC 690.13 |
| PV warning labels | NEC 690.31 |
| Breaker sizing | NEC 705.12 |
| Max DC voltage (≤600V residential) | NEC 690.7 |
| NEC code version stated on plan | General |

---

## Disclaimer

This tool is advisory only. Final approval is the responsibility of the licensed plan reviewer or AHJ. Always verify against the applicable code edition.
