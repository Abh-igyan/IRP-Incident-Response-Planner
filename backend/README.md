# Traffic Incident Response Planning

FastAPI + SQLite + Leaflet application for traffic incident response planning.

## Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main --reload
```

Open `http://127.0.0.1:8000`.

## API

- `POST /predict`: predicts closure probability, impact, resources, response priority, traffic forecast, and diversion plan.
- `POST /feedback`: stores operational feedback in `backend/data/feedback.sqlite3`.
- `GET /options`: returns dropdown values discovered from the historical incident dataset.
- `GET /health`: basic service health check.

## Notes

- Model, metadata, dataset, and graph files are loaded once during FastAPI startup.
- Corridor, zone, and police station are derived from the nearest historical incident location.
- The CatBoost model is used when `catboost` is installed. If the pickle cannot be loaded, the backend falls back to the saved metadata risk maps so the application remains runnable.
- Mappls validation is optional. Set `MAPPLS_ACCESS_TOKEN` to enable route validation; otherwise the local graph route is used.
