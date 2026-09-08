import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def make_engine():
    user = os.getenv("DB_USER", "etl_user")
    password = os.getenv("DB_PASS", "etl_pass")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME", "etl_demo")
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
    engine = create_engine(url, pool_pre_ping=True)
    return engine
