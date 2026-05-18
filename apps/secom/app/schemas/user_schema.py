from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    password: str
    nickname: str
    email: str
    role: str