from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import os
import time
import sqlite3
import hashlib
import hmac
import secrets
import jwt
from pathlib import Path

router = APIRouter()

DB_PATH = (Path(__file__).resolve().parents[1] / 'data.sqlite3').as_posix()
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-env')
JWT_EXPIRES_DAYS = int(os.getenv('JWT_EXPIRES_DAYS', '7'))

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.execute(
    'CREATE TABLE IF NOT EXISTS users ('
    'id INTEGER PRIMARY KEY AUTOINCREMENT,'
    'phone TEXT UNIQUE NOT NULL,'
    'name TEXT UNIQUE NOT NULL,'
    'password_hash TEXT NOT NULL,'
    'password_salt TEXT NOT NULL,'
    'created_at INTEGER NOT NULL'
    ')'
)
_conn.commit()

class RegisterRequest(BaseModel):
    phone: str
    name: str
    password: str

class LoginRequest(BaseModel):
    phoneOrName: str
    password: str

def _valid_phone(phone: str) -> bool:
    return phone.isdigit() and 6 <= len(phone) <= 15

def _valid_name(name: str) -> bool:
    return bool(name) and len(name) <= 32

def _valid_password(password: str) -> bool:
    return len(password) >= 6

def _hash_password(password: str):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return salt.hex(), dk.hex()

def _verify_password(salt_hex: str, hash_hex: str, password: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return hmac.compare_digest(dk.hex(), hash_hex)

def _create_token(user_id: int, name: str) -> str:
    exp = int(time.time()) + JWT_EXPIRES_DAYS * 86400
    payload = {'sub': str(user_id), 'name': name, 'exp': exp}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def _decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        raise HTTPException(status_code=401, detail='invalid_token')

def _get_user_by_identifier(identifier: str):
    cur = _conn.execute(
        'SELECT id, phone, name, password_hash, password_salt FROM users WHERE phone=? OR name=? LIMIT 1',
        (identifier, identifier)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        'id': row[0],
        'phone': row[1],
        'name': row[2],
        'password_hash': row[3],
        'password_salt': row[4],
    }

def _get_user_by_id(user_id: int):
    cur = _conn.execute(
        'SELECT id, phone, name FROM users WHERE id=? LIMIT 1',
        (user_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {'id': row[0], 'phone': row[1], 'name': row[2]}

@router.post('/register', status_code=201)
async def register(req: RegisterRequest):
    phone = req.phone.strip()
    name = req.name.strip()
    password = req.password

    if not _valid_phone(phone):
        raise HTTPException(status_code=400, detail='invalid_phone')
    if not _valid_name(name):
        raise HTTPException(status_code=400, detail='invalid_name')
    if not _valid_password(password):
        raise HTTPException(status_code=400, detail='invalid_password')

    cur = _conn.execute('SELECT 1 FROM users WHERE phone=? OR name=?', (phone, name))
    if cur.fetchone():
        raise HTTPException(status_code=409, detail='user_exists')

    salt_hex, hash_hex = _hash_password(password)
    now = int(time.time())
    _conn.execute(
        'INSERT INTO users (phone, name, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?, ?)',
        (phone, name, hash_hex, salt_hex, now)
    )
    _conn.commit()

    cur = _conn.execute('SELECT id, phone, name FROM users WHERE phone=?', (phone,))
    row = cur.fetchone()
    return {'id': row[0], 'phone': row[1], 'name': row[2]}

@router.post('/login')
async def login(req: LoginRequest):
    identifier = req.phoneOrName.strip()
    password = req.password

    user = _get_user_by_identifier(identifier)
    if not user:
        raise HTTPException(status_code=401, detail='invalid_credentials')
    if not _verify_password(user['password_salt'], user['password_hash'], password):
        raise HTTPException(status_code=401, detail='invalid_credentials')

    token = _create_token(user['id'], user['name'])
    return {
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'phone': user['phone']}
    }

def _auth_user(request: Request):
    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if not auth or not auth.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='missing_auth')
    token = auth.split(' ', 1)[1].strip()
    payload = _decode_token(token)
    uid = int(payload.get('sub'))
    user = _get_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=401, detail='invalid_user')
    return user

@router.get('/me')
async def me(user = Depends(_auth_user)):
    return user