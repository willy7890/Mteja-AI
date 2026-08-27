from pydantic import BaseModel, EmailStr

class CustomerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    organization_id: int

class CustomerLoginRequest(BaseModel):
    email: EmailStr
    password: str

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    organization_id: int

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"