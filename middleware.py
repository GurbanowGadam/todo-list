import sys
import jwt
from fastapi import status, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp
from fastapi.responses import JSONResponse

from configData import ConfigData
from helper import Constants

sys.path.append('..')

class TokenAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in Constants.URLS_OF_NOT_REQUIRE_TOKEN:
            token = request.headers.get("Authorization")
            if token is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"status": False, "message": "Authorization token missing"}
                )

            try:
                token = token.split(" ")[1]
                decoded_token = jwt.decode(token, ConfigData.SECRET_KEY_LOGIN, algorithms=[ConfigData.ALGORITHM])
                request.state.user = decoded_token
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"status": False, "message": "Token has expired"}
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"status": False, "message": "Invalid token"}
                )

        return await call_next(request)