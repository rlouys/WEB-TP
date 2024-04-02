from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from .database import Base
from datetime import datetime

# Classe permettant de représenter un livre et de générer un formulaire avec cette classe.
# Utilisée dans dans la fonction modifier_livre de la route /liste dans main.py

class Livre(Base):
    __tablename__ = 'livres'

    id: Mapped[int] = Column(Integer, primary_key=True)
    nom: Mapped[str] = Column(String(128), nullable=False)
    auteur: Mapped[str] = Column(String(128), nullable=False)
    editeur: Mapped[str] = Column(String(72), nullable=False)
    createdOn: Mapped[datetime] = Column(DateTime, nullable=False, server_default=func.now())
    created_by: Mapped[int] = Column(Integer, ForeignKey('users.id'), nullable=False)
    modified_on: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    modified_by: Mapped[int] = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship("User", foreign_keys=[created_by], backref="created_livres")
    modifier = relationship("User", foreign_keys=[modified_by], backref="modified_livres")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column(String(20), unique=True, nullable=False)
    email: Mapped[str] = Column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = Column(String(128))
    privileges: Mapped[str] = Column(String(120))
    date_added: Mapped[datetime] = Column(DateTime, server_default=func.now())
