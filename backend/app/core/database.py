from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.db_url.startswith("sqlite") else {}
engine = create_engine(settings.db_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_backward_compatible_schema() -> None:
    """Small startup migration helper for local/demo DBs.

    Keeps old SQLite databases functional when new columns are introduced.
    """

    inspector = inspect(engine)
    if "findings" not in inspector.get_table_names():
        return

    existing_columns = {c["name"] for c in inspector.get_columns("findings")}
    required = {
        "cvss_score": "REAL DEFAULT 0.0",
        "cvss_severity": "VARCHAR(16) DEFAULT 'low'",
        "cwe_name": "VARCHAR(255)",
    }

    if settings.db_url.startswith("sqlite"):
        with engine.begin() as conn:
            for column, ddl in required.items():
                if column not in existing_columns:
                    conn.execute(text(f"ALTER TABLE findings ADD COLUMN {column} {ddl}"))
