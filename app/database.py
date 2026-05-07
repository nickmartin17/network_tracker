from sqlalchemy import inspect, text
from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///./network.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    from .models import Contact, Interaction, User

    SQLModel.metadata.create_all(engine)
    _migrate_sqlite_schema()


def _migrate_sqlite_schema() -> None:
    if engine.url.get_backend_name() != "sqlite":
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "contact" in table_names:
            contact_columns = {column["name"] for column in inspector.get_columns("contact")}
            if "priority" not in contact_columns:
                connection.execute(text("ALTER TABLE contact ADD COLUMN priority VARCHAR"))

        if "interaction" in table_names:
            interaction_columns = {column["name"] for column in inspector.get_columns("interaction")}
            if "follow_up_notes" not in interaction_columns:
                connection.execute(text("ALTER TABLE interaction ADD COLUMN follow_up_notes VARCHAR"))


def get_session() -> Session:
    return Session(engine)
