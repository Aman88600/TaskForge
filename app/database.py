from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

YOUR_PASSWORD = os.getenv("psql_password")
DATABASE_URL = f"postgresql+psycopg://postgres:{YOUR_PASSWORD}@localhost:5432/taskforge"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)