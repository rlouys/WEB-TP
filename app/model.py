from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional
#from .database import Base
from enum import Enum

# Classe permettant de représenter un livre et de générer un formulaire avec cette classe.
# Utilisée dans dans la fonction modifier_livre de la route /liste dans main.py

class Livre(BaseModel):
    id: int
    nom: str = Field(..., min_length=1)
    auteur: str = Field(..., min_length=1)
    editeur: str = Field(..., min_length=1, error_messages={"missing":"Hey"})

    @validator('nom', 'auteur','editeur')
    def non_vide(cls, v):
        print("ok")
        if not v or v.isspace() or v == "":
            print("nok")
            raise ValueError("Le champ doit être rempli")
        return v