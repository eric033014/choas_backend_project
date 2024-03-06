from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# sqlalchemy 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# pydantic
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str
    email: str
    password: str

class UserPatchUpdate(BaseModel):
    name: str = None
    email: str = None
    password: str = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

# CRUD
def create_user(db, user):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()

def update_user(db, user_id, user_data):
    user = db.query(User).filter(User.id == user_id).first()

    for key, value in user_data.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    user = db.query(User).filter(User.id == user_id).first()
    return user

def delete_user(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
    
def get_users(db, skip: int = 0, limit: int = 10, sort_by: str = None):
    query = db.query(User)
    if sort_by:
        if sort_by.startswith("-"):
            query = query.order_by(getattr(User, sort_by[1:]).desc())
        else:
            query = query.order_by(getattr(User, sort_by))
    return query.offset(skip).limit(limit).all()