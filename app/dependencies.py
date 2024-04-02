from .database import SessionLocal

#############################
# PERMET DE RECUPÉRER LA DB #
#############################
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
