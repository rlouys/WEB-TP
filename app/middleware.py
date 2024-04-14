from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class AddUsernameToRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Vous pourriez récupérer le nom d'utilisateur d'un cookie ou d'une autre manière de stockage
        username = request.cookies.get("username", "Utilisateur")
        request.state.username = username  # Ajouter le nom d'utilisateur à l'état de la requête pour y accéder globalement
        response = await call_next(request)
        return response
