# this is the database file that controls the db url, engine, session dependency,
# and table initialization
# resources uses: https://fastapi.tiangolo.com/tutorial/sql-databases/

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///thermostat.db"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session