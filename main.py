from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from utils.jwt import *
from utils.users import *

# initial
app = FastAPI()


# SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserResponse)
def create_user_api(user: UserCreate, db = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    current_user_create = user.dict()
    del current_user_create['password']
    current_user_create['hashed_password'] = get_password_hash(user.password)
    return create_user(db, User(**current_user_create))

@app.get("/users/", response_model=List[UserResponse])
def read_users_api(skip: int = 0, limit: int = 10, sort_by: Optional[str] = None):
    db = SessionLocal()
    return get_users(db, skip, limit, sort_by)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user_api(user_id: int, db = Depends(get_db)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user_api(user_id: int, user: UserUpdate, db = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    current_user_create = user.dict()
    if 'password' in current_user_create:
        del current_user_create['password']
        current_user_create['hashed_password'] = get_password_hash(user.password)
    return update_user(db, user_id, user.dict())

@app.patch("/users/{user_id}", response_model=UserResponse)
def patch_update_user_api(user_id: int, user: UserPatchUpdate, db = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    current_user_update = user.dict()
    if 'password' in current_user_update and current_user_update['password']:
        del current_user_update['password']
        current_user_update['hashed_password'] = get_password_hash(user.password)
    return update_user(db, user_id, current_user_update)

@app.delete("/users/{user_id}")
def delete_user_api(user_id: int, db = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}

# jwt related
@app.post("/login/")
def login_for_access_token(login_user: UserLogin, db = Depends(get_db)):
    user = authenticate_user(db, login_user.email, login_user.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": "Bearer " + access_token }

# routers need authenticate user
@app.get("/users/me/", response_model=UserResponse)
def read_users_me(request: Request, db = Depends(get_db)):
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = decode_access_token(authorization.replace("Bearer ",""))
    if not token or not token.get("sub"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    email = token.get("sub")
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user