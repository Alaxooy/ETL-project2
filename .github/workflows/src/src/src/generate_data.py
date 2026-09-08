#!/usr/bin/env python3
"""
Generate synthetic transactional data and write CSVs to data/.
"""
import csv
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_customers(n_customers=50):
    customers = []
    for i in range(n_customers):
        customers.append({
            "customer_id": f"C{1000+i}",
            "name": fake.name(),
            "country": fake.country()
        })
    return customers

def generate_products(n_products=40):
    products = []
    for i in range(n_products):
        products.append({
            "stock_code": f"P{1000+i}",
            "description": fake.word().title(),
            "unit_price": round(random.uniform(1.0, 200.0), 2)
        })
    return products

def generate_transactions(days=7, tx_per_day=100, customers=None, products=None, seed=None):
    if seed is not None:
        random.seed(seed)
    transactions = []
    start_date = datetime.now() - timedelta(days=days)
    invoice_seq = 1
    for d in range(days):
        day = start_date + timedelta(days=d)
        for t in range(tx_per_day):
            invoice_no = f"INV-{day.strftime('%Y%m%d')}-{invoice_seq}"
            invoice_seq += 1
            product = random.choice(products)
            customer = random.choice(customers)
            quantity = random.randint(1, 10)
            invoice_date = day + timedelta(
                hours=random.randint(0,23),
                minutes=random.randint(0,59),
                seconds=random.randint(0,59)
            )
            transactions.append({
                "invoice_no": invoice_no,
                "stock_code": product["stock_code"],
                "description": product["description"],
                "quantity": quantity,
                "invoice_date": invoice_date.isoformat(sep=' '),
                "unit_price": product["unit_price"],
                "customer_id": customer["customer_id"],
                "country": customer["country"]
            })
    return transactions

def write_csv(filename, rows, fieldnames):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path

def generate_all(data_days=7, tx_per_day=100, n_customers=50, n_products=40, seed=None):
    customers = generate_customers(n_customers)
    products = generate_products(n_products)
    tx = generate_transactions(days=data_days, tx_per_day=tx_per_day, customers=customers, products=products, seed=seed)
    cust_path = write_csv("customers.csv", customers, ["customer_id", "name", "country"])
    prod_path = write_csv("products.csv", products, ["stock_code", "description", "unit_price"])
    tx_path = write_csv("transactions.csv", tx, ["invoice_no","stock_code","description","quantity","invoice_date","unit_price","customer_id","country"])
    return {"customers": cust_path, "products": prod_path, "transactions": tx_path}

if __name__ == "__main__":
    paths = generate_all(data_days=7, tx_per_day=200, seed=42)
    print("Generated files:", paths)
