from pydantic import BaseModel, EmailStr


# Schema used when a new user creates an account.
# Registration requires email, password, and name.
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


# Schema used when an existing user logs in.
# Login only requires email and password.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema returned to the client.
# Password and password_hash are intentionally excluded.
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

    model_config = {
        "from_attributes": True
    }