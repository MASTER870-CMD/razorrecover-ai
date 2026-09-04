import os
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./razorrecover.db")

# SQLite needs check_same_thread=False for multi-threaded FastAPI
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from database.schema.models import Base, SystemSettings

    Base.metadata.create_all(bind=engine)

    # Seed default system settings if not already present
    with get_db_session() as session:
        settings = session.query(SystemSettings).filter_by(id="default").first()
        if not settings:
            default_settings = SystemSettings(
                id="default",
                automatic_recovery_enabled=True,
                max_retry_attempts=3,
                max_automatic_amount=25000.0,
                human_approval_threshold=0.70,
                recovery_window_days=14,
                max_contact_attempts=2,
                retry_cooldown_minutes=60,
            )
            session.add(default_settings)
            session.commit()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
