from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  # Adjusted import here

# DB Configuration
DATABASE_URL = "sqlite:///app/data/database.sqlite"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Only necessary for SQLite
    echo=False  # If you want to see the generated SQL statements
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Generate base class for declarative classes from the data (Class parameter in model.py)
Base = declarative_base()  # Adjusted to call declarative_base()

def create_database():
    Base.metadata.create_all(engine)

