from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Secret key pour signer le JWT
SECRET_KEY = "me5GjOLMAQDzFBijhZ9NosTNlkS0J5SH"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    exception_de_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise exception_de_credentials
        return payload  # Retour du payload complet pour plus de flexibilité
    except JWTError:
        raise exception_de_credentials

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_token(token)
    return payload  # Nous pouvons maintenant utiliser n'importe quelle partie du payload dans nos fonctions de point de terminaison