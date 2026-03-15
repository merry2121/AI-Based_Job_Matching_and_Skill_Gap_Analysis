from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "seeker" or "employer"
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)   # token for password reset
    reset_token_expiry = Column(DateTime, nullable=True)  # expiration