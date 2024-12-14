import hashlib
import os

# Генерация хэша пароля
def hash_password(password):
    salt = os.urandom(16)  # Генерируем случайную соль
    salted_password = salt + password.encode("utf-8")
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return f"{salt.hex()}:{hashed_password}"

# Проверка пароля
def verify_password(stored_password, provided_password):
    salt, stored_hash = stored_password.split(":")
    salted_password = bytes.fromhex(salt) + provided_password.encode("utf-8")
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password == stored_hash
