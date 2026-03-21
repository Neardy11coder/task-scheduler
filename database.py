from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class TaskModel(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    priority    = Column(Integer, nullable=False)
    category    = Column(String, default="General")
    deadline    = Column(String, nullable=True)
    created_at  = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    completed   = Column(Integer, default=0)   # 0 = pending, 1 = done


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise