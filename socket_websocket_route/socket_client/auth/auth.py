import os
import jwt  # used for encoding and decoding jwt tokens
from fastapi import HTTPException  # used to handle error handling
from passlib.context import CryptContext  # used for hashing the password
from datetime import datetime, timedelta  # used to handle expiry time for tokens
# from secret import auth_key 
auth_key = "b7141fe63070539928483ae8df69df077fb4a41fd49b0438cdef99f7a6b0e110"


class Auth:
    hasher = CryptContext(schemes=['bcrypt'])
    # secret = os.getenv("APP_SECRET_STRING")
    secret = auth_key

    def encode_data(self, password):
        return self.hasher.hash(password)

    def verify_data(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

