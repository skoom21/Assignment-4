import hashlib
from cryptography.fernet import Fernet
import sqlite3
from datetime import datetime
from typing import Optional


DB = 'hospital.db'


# Simple deterministic anonymization using SHA256 (non-reversible)
def anonymize_name(name: str) -> str:
    h = hashlib.sha256(name.encode()).hexdigest()[:8]   
    return f'ANON_{h}'


# Mask phone numbers: keep last 4 digits
def mask_contact(contact: str) -> str:
    digits = ''.join(ch for ch in contact if ch.isdigit())
    if len(digits) >= 4:
        last4 = digits[-4:]
    else:
        last4 = digits
    return f'XXX-XXX-{last4}'


# Password hashing
def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


# Logging helper
def log_action(user_id: Optional[int], username: str, role: str, action: str, details: str=''):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    ts = datetime.utcnow().isoformat()
    c.execute('INSERT INTO logs (user_id, username, role, action, timestamp, details) VALUES (?, ?, ?, ?, ?, ?)',
    (user_id, username, role, action, ts, details))
    conn.commit()
    conn.close()


# Optional: Fernet utilities 
def generate_fernet_key() -> bytes:
    return Fernet.generate_key()


def get_fernet_cipher(key: bytes) -> Fernet:
    return Fernet(key)


def fernet_encrypt(cipher: Fernet, plaintext: str) -> bytes:
    return cipher.encrypt(plaintext.encode())


def fernet_decrypt(cipher: Fernet, token: bytes) -> str:
    return cipher.decrypt(token).decode()