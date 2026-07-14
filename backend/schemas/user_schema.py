from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    model_config = {'from_attributes': True}

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
