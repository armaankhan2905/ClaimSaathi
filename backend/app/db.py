from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

settings = get_settings()

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session_factory() -> sessionmaker:
    """For background work that outlives the request (overridden in tests)."""
    return SessionLocal


def init_db(bind=None) -> None:
    from . import models  # noqa: F401  (registers tables)

    bind = bind or engine
    Base.metadata.create_all(bind=bind)
    add_missing_columns(bind)


def add_missing_columns(bind) -> list[str]:
    """Add columns that newer code expects to tables created by older code.

    `create_all` makes new tables but never changes existing ones, so a database from an
    earlier stage would miss new columns. New columns are always nullable or have a simple
    default, so a plain ADD COLUMN is enough. Returns "table.column" for each one added.
    """
    added: list[str] = []
    insp = inspect(bind)
    existing_tables = set(insp.get_table_names())
    with bind.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            have = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name in have:
                    continue
                ddl = f'ALTER TABLE {table.name} ADD COLUMN "{col.name}" {col.type.compile(bind.dialect)}'
                default = col.default.arg if col.default is not None and col.default.is_scalar else None
                if default is not None:
                    if isinstance(default, bool):
                        default = ("1" if default else "0") if bind.dialect.name == "sqlite" else str(default).lower()
                    elif isinstance(default, str):
                        default = "'" + default.replace("'", "''") + "'"
                    ddl += f" DEFAULT {default}"
                conn.execute(text(ddl))
                added.append(f"{table.name}.{col.name}")
    return added
