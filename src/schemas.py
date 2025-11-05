from pydantic import BaseModel

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    """Schema used for creating a new user (requires password)."""
    password: str

class UserRead(UserBase):
    """Schema used for reading/returning user data (no password)."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True # Replaces orm_mode = True