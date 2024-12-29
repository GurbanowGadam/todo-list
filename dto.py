from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class UserRegisterCheck(BaseModel):
    token: str

class UserLogin(BaseModel):
    email: str
    password: str

class AddTodo(BaseModel):
    title: str
    description: str
    amount: float

class UpdateTodo(BaseModel):
    id: int
    title: str
    description: str
    amount: float
    is_completed: bool

class UpdateTodoStatus(BaseModel):
    id: int
    is_completed: bool

class DeleteTodo(BaseModel):
    id: int