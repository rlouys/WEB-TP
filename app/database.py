from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#############
# DB IMPORT #
#############

# DATABASE_URL = "sqlite:///./users.db"

#engine = create_engine(
#    DATABASE_URL, connect_args={"check_same_thread": False}  # Required for SQLite
#)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Permet de générer des classes depuis la base de donnée (Paramètre de classe dans model.py)
#Base = declarative_base()
