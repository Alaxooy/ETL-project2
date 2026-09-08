# etl-project

Demo ETL project showcasing synthetic data generation, transformation, and load into MySQL, with a small FastAPI service for metrics.

Quickstart (after files are in this repo)

1. Install Python dependencies
   python -m pip install --upgrade pip
   pip install -r requirements.txt

2. Start MySQL using Docker (install Docker Desktop first)
   docker-compose up -d
   Wait ~20–30s for MySQL to become ready.

3. Create the database schema
   docker exec -i $(docker ps -qf "ancestor=mysql:8.0") mysql -u root -prootpassword etl_demo < sql/schema.sql

4. Configure env
   cp .env.example .env

5. Generate data and run the ETL (module mode)
   python -m src.etl --generate --num-days 3 --tx-per-day 100

6. Start the FastAPI server
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

   - Health: http://localhost:8000/health
   - Revenue: http://localhost:8000/metrics/revenue
   - Top customers: http://localhost:8000/metrics/top-customers

Run tests:
   pytest -q

Notes
- The ETL writes to a staging table then merges into `transactions`. The schema enforces UNIQUE(invoice_no, stock_code) so re-running the ETL is idempotent.
- If Docker maps MySQL to a different host port, update `.env` accordingly.
