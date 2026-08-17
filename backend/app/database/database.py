"""
database.py
------------
Sets up the SQLAlchemy engine, session factory, and declarative base for
SQLite.

WHAT are we doing?
    Creating the low-level plumbing SQLAlchemy needs: an `engine`
    (connection to the SQLite file), a `SessionLocal` factory (creates a
    new DB session per request), and a `Base` class that our ORM models
    inherit from.

WHY SQLite?
    Zero setup — it's a single file, no separate database server needed.
    Perfect for a portfolio project and local development. The code is
    written using SQLAlchemy, so swapping to Postgres later would mostly
    mean changing DATABASE_URL.

WHICH file:
    backend/app/database/database.py

HOW it connects to other files:
    - models.py imports `Base` to define the PredictionHistory table.
    - crud.py and API routes import `get_db` as a FastAPI dependency to
      get a database session per-request.
    - main.py calls Base.metadata.create_all() at startup to create
      tables if they don't exist yet.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI may handle a request in a different thread than the one
# that created the connection.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and always closes it after
    the request, even if an error occurs."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
