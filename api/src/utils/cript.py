import json
import bcrypt
from typing import Dict

class CriptDict:
    @staticmethod
    def generate_salt() -> bytes:
        return bcrypt.gensalt()
    
    @staticmethod
    def to_bytes(salt: str) -> bytes:
        return salt.encode('utf-8')

    @staticmethod
    def hash_password(password: str, salt: bytes) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))