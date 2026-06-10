import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./envirofix.db"  # fallback for local dev without Docker
)

# Fix for SQLAlchemy + PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    scan_type  = Column(String(50))
    status     = Column(String(20))
    data       = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Alert(Base):
    __tablename__ = "alerts"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    severity    = Column(String(20))
    title       = Column(String(200))
    detail      = Column(Text)
    tool        = Column(String(100))
    fix         = Column(Text)
    risk_level  = Column(String(20))
    ai_analysis = Column(Text)
    resolved    = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.now)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialised.")

if __name__ == "__main__":
    init_db()
