from __future__ import annotations

from src.db.models import Base
from src.db.session import engine


def init_schema() -> None:
    Base.metadata.create_all(bind=engine)

