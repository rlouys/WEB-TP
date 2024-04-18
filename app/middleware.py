from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.model import *

from app.login_manager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, oauth2_scheme, \
    verify_token, get_user_id_from_token

from app.data.dependencies import get_db

class AddUsernameToRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Vous pourriez récupérer le nom d'utilisateur d'un cookie ou d'une autre manière de stockage
        is_authenticated = request.cookies.get('is_authenticated')
        # username = request.cookies.get("username", "Utilisateur")
        privileges =''
        response = None
        db: Session = next(get_db())

        try:
            username = 'Utilisateur'
            token = request.cookies.get('access_token')
            if token:
                token = token[7:]  # Assume you're stripping 'Bearer ' or similar prefix
                if verify_token(token):
                    user_id = get_user_id_from_token(token)
                    userFromToken = db.query(User).filter(User.id == user_id).first()
                    if userFromToken:
                        username = userFromToken.username.capitalize()
                        if userFromToken.privileges == 'admin':
                            privileges = userFromToken.privileges
                            print(privileges)

            request.state.username = username
            request.state.is_authenticated = is_authenticated
            request.state.privileges = privileges
            response = await call_next(request)
        finally:
            db.close()

        return response
