from app.data import database
from app.schemas import UserSchema


def get_user_by_username(username: str):
    for user in database['users']:
        if user['username'] == username:
            return UserSchema.model_validate(user)
    return None

def get_user_by_email(email: str):
    for user in database['users']:
        if user['email'] == email:
            return UserSchema.model_validate(user)
    return None

def get_user_by_id(id: str):
    for user in database['users']:
        if user['id'] == id:
            return UserSchema.model_validate(user)
    return None
