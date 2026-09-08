import os
from src.generate_data import generate_all
import csv

def test_generate_creates_csv(tmp_path):
    # generate to data dir (default), but assert structure works
    paths = generate_all(data_days=2, tx_per_day=10, n_customers=5, n_products=5, seed=1)
    tx_path = paths["transactions"]
    assert os.path.exists(tx_path)
    with open(tx_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) > 0
    # expect required columns
    for col in ("invoice_no", "stock_code", "quantity", "invoice_date"):
        assert col in rows[0]
