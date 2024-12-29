import uvicorn
from fastapi import FastAPI

import models
from database import engine
from routers import todos, auth
from middleware import TokenAuthMiddleware
from helper import custom_openapi

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.openapi = lambda: custom_openapi(app)

app.add_middleware(TokenAuthMiddleware)

app.include_router(auth.router)
app.include_router(todos.router)

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
