from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings
import os

# Default to Postgres, but allow SQLite for testing migrations/connectivity in isolated environments
url = os.environ.get("USE_TEST_DB_URL", settings.DATABASE_URL)

engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
