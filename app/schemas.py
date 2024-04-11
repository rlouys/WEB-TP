from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: str
    username: str
    email: EmailStr
    password: str


class UserSignUp(BaseModel):
    new_username: str
    new_email: EmailStr
    new_password: str
    confirm_password: str
