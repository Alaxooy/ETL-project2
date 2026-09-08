from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from src.db import make_engine
from datetime import datetime

app = FastAPI(title="ETL Project Metrics API")
engine = make_engine()

class RevenueResponse(BaseModel):
    revenue: float

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics/revenue", response_model=RevenueResponse)
async def total_revenue(start: str = None, end: str = None):
    """Return total revenue (quantity * unit_price). Optional ISO datetimes for start/end."""
    params = {}
    where = []
    if start:
        try:
            datetime.fromisoformat(start)
            where.append("invoice_date >= :start")
            params["start"] = start
        except Exception:
            raise HTTPException(status_code=400, detail="invalid start datetime")
    if end:
        try:
            datetime.fromisoformat(end)
            where.append("invoice_date <= :end")
            params["end"] = end
        except Exception:
            raise HTTPException(status_code=400, detail="invalid end datetime")
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""
    q = text(f"SELECT COALESCE(SUM(quantity * unit_price), 0) as revenue FROM transactions {where_clause};")
    with engine.begin() as conn:
        res = conn.execute(q, params).fetchone()
    return {"revenue": float(res[0])}

@app.get("/metrics/top-customers")
async def top_customers(limit: int = 10):
    q = text("SELECT customer_id, SUM(quantity * unit_price) AS revenue FROM transactions GROUP BY customer_id ORDER BY revenue DESC LIMIT :limit;")
    with engine.begin() as conn:
        rows = conn.execute(q, {"limit": limit}).fetchall()
    return [{"customer_id": r[0], "revenue": float(r[1] or 0)} for r in rows]
