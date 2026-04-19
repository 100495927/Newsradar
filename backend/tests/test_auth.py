import pytest
from datetime import timedelta
from jose import jwt

# Importamos las funciones de tu fichero (ajusta la ruta según tu estructura)
from app.auth.jwt_utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    decode_access_token,
    SECRET_KEY,
    ALGORITHM
)

# --- TESTS UNITARIOS (Aislados al 100%) ---

def test_hash_and_verify_password():
    """Prueba que la contraseña se encripta y se verifica correctamente"""
    plain_password = "mi_password_segura_123"
    hashed = hash_password(plain_password)
    
    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True
    assert verify_password("password_incorrecta", hashed) is False

def test_create_and_decode_access_token():
    """Prueba que el token JWT se genera y se decodifica bien con el user_id"""
    user_id = 99
    token = create_access_token(user_id)
    
    assert isinstance(token, str)
    
    # Verificamos que al decodificar, recuperamos el user_id correcto
    decoded_id = decode_access_token(token)
    assert decoded_id == user_id

def test_decode_invalid_token():
    """Prueba que un token inventado lanza error"""
    with pytest.raises(jwt.JWTError):
        decode_access_token("este.token.es_falso")