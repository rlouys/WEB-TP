from pydantic import EmailStr
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.data.database import Base
from datetime import datetime

# Classe permettant de représenter un livre et de générer un formulaire avec cette classe.
# Utilisée dans dans la fonction modifier_livre de la route /liste dans main.py

class Livre(Base):
    __tablename__ = 'livres'

    id: Mapped[int] = Column(Integer, primary_key=True)
    nom: Mapped[str] = Column(String(128), nullable=False)
    auteur: Mapped[str] = Column(String(128), nullable=False)
    editeur: Mapped[str] = Column(String(72), nullable=False)
    price: Mapped[float] = Column(Float, nullable=False, server_default="0.0")
    stock: Mapped[int] = Column(Integer, nullable=False, server_default="0")
    createdOn: Mapped[datetime] = Column(DateTime, nullable=False, server_default=func.now())
    created_by: Mapped[int] = Column(Integer, ForeignKey('users.id'), nullable=False)
    modified_on: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    modified_by: Mapped[int] = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner_id: Mapped[int] = Column(Integer, ForeignKey('users.id'))

    # FOREIGN KEYS
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_books")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_livres")
    modifier = relationship("User", foreign_keys=[modified_by], back_populates="modified_livres")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = Column(String(20), unique=True, nullable=False)
    email: Mapped[str] = Column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = Column(String(128))
    privileges: Mapped[str] = Column(String(120))
    date_added: Mapped[datetime] = Column(DateTime, server_default=func.now())

    # FOREIGN KEYS
    owned_books = relationship("Livre", foreign_keys="[Livre.owner_id]", back_populates="owner")  # Relation to track all books owned by the user
    created_livres = relationship("Livre", foreign_keys="[Livre.created_by]", back_populates="creator")
    modified_livres = relationship("Livre", foreign_keys="[Livre.modified_by]", back_populates="modifier")
