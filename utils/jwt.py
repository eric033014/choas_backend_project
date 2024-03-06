from jose import JWTError, jwt

# jwt setting
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# create jwt token
def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# parse jwt token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None