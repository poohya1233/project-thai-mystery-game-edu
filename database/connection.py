import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL in environment or .env file")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # เช็ก connection ก่อนใช้งานจริง ลดปัญหา connection หลุดค้าง
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency สำหรับ FastAPI เพื่อเปิดและปิด DB Session ต่อ 1 Request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()