#!/usr/bin/env python3
"""
ETL pipeline:
- Optionally generates synthetic data
- Reads transactions CSV, basic transforms and QA
- Loads into staging table then merges into final table with INSERT IGNORE

Run as module:
  python -m src.etl --generate --num-days 3 --tx-per-day 100
"""
import os
import click
import logging
import pandas as pd
from sqlalchemy import text
from src.db import make_engine
from src.generate_data import generate_all

logging.basicConfig(level=logging.INFO)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names
    df = df.rename(columns=lambda c: c.strip().lower())
    # Parse dates
    if "invoice_date" in df.columns:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    # Drop rows missing invoice_no or stock_code
    df = df.dropna(subset=["invoice_no", "stock_code"])
    # Fill and cast
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    # Additional derived columns can be added here
    return df

@click.command()
@click.option("--generate", is_flag=True, help="Generate synthetic data before running ETL")
@click.option("--num-days", default=7, help="When generating: number of days")
@click.option("--tx-per-day", default=100, help="When generating: transactions per day")
@click.option("--source", default=None, help="Path to transactions CSV (overrides generate)")
def run_etl(generate, num_days, tx_per_day, source):
    if source is None and generate:
        logging.info("Generating synthetic data...")
        paths = generate_all(data_days=num_days, tx_per_day=tx_per_day, seed=42)
        source = paths["transactions"]
    if source is None:
        raise click.UsageError("Either --source or --generate must be provided")

    logging.info("Reading transactions from %s", source)
    df = pd.read_csv(source)
    logging.info("Read %d rows", len(df))

    df = transform_df(df)
    logging.info("After transform: %d rows", len(df))

    engine = make_engine()
    with engine.begin() as conn:
        # load staging (replace each run)
        logging.info("Writing staging table (staging_transactions)")
        df.to_sql("staging_transactions", con=conn, if_exists="replace", index=False, method="multi")
        logging.info("Merging staging into transactions (idempotent)")
        # Insert ignoring duplicates based on unique key defined in schema
        conn.execute(text("""
            INSERT IGNORE INTO transactions
              (invoice_no, stock_code, description, quantity, invoice_date, unit_price, customer_id, country)
            SELECT invoice_no, stock_code, description, quantity, invoice_date, unit_price, customer_id, country
            FROM staging_transactions;
        """))
        logging.info("Merge complete")

if __name__ == "__main__":
    run_etl()
