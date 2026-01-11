from passlib.context import CryptContext
from PIL import Image
import io
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # Legacy support for plain text passwords (from reset_db.py)
    if plain_password == hashed_password:
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def process_image_to_webp(file_content: bytes, destination_dir: Path, filename_prefix: str) -> str:
    """
    Yüklenen herhangi bir resmi WebP formatına çevirir ve kaydeder.
    """
    # Klasörü oluştur
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    # Resmi aç
    image = Image.open(io.BytesIO(file_content))
    
    # Dosya ismini oluştur
    new_filename = f"{filename_prefix}.webp"
    file_path = destination_dir / new_filename
    
    # WebP olarak kaydet
    image.save(file_path, "WEBP", quality=80, method=6)
    
    return new_filename
