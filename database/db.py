import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./document_ai.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from database import models

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
