from datetime import datetime, timedelta, UTC
from jose import jwt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

SECRET_KEY = 'CHANGE_ME_IN_PRODUCTION'
ALGORITHM = 'HS256'

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload['exp'] = datetime.now(UTC) + timedelta(days=1)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
