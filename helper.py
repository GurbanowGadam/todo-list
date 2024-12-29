from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.openapi.utils import get_openapi

from configData import ConfigData

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Helper():
    def get_password_hash(password):
        return bcrypt_context.hash(password)

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, secreteKeyRegister: str = ConfigData.SECRET_KEY_LOGIN):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secreteKeyRegister, algorithm=ConfigData.ALGORITHM)
        return encoded_jwt
    
    def verify_password(plain_password, hashed_password):
        return bcrypt_context.verify(plain_password, hashed_password)

class Constants():
    URLS_OF_NOT_REQUIRE_TOKEN = ["/auth/user-login", "/auth/user-register", "/auth/user-register-check", "/docs", "/openapi.json"]

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Token Test API",
        version="1.0.0",
        description="This is a test API with Bearer Token Authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
