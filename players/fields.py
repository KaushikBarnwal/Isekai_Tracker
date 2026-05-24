import base64
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet

def get_cipher():
    secret = settings.SECRET_KEY
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    # ensure it's at least 32 bytes
    if len(secret) < 32:
        secret = secret.ljust(32, b'*')
    key = base64.urlsafe_b64encode(secret[:32])
    return Fernet(key)

class EncryptedTextField(models.TextField):
    def get_prep_value(self, value):
        if not value:
            return value
        # If it's already encrypted, don't double encrypt
        if value.startswith('gAAAAA'):
            return value
        cipher = get_cipher()
        return cipher.encrypt(value.encode('utf-8')).decode('utf-8')
    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        cipher = get_cipher()
        try:
            return cipher.decrypt(value.encode('utf-8')).decode('utf-8')
        except Exception:
            # Fallback for unencrypted legacy data
            return value
    def to_python(self, value):
        return value
