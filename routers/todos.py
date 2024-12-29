import sys
import models
import dto

from fastapi import Depends, APIRouter, status, Request
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


sys.path.append('..')

router = APIRouter(
    prefix='/todos',
    tags=['Todos'],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Not found'
        }
    }
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post('/add-todo', response_class=JSONResponse)
async def addTodo(request: Request, addTodo: dto.AddTodo, db: Session = Depends(get_db)):
    try:
        userId = request.state.user["id"]

        todo = models.Todos()
        todo.title = addTodo.title
        todo.description = addTodo.description
        todo.amount = addTodo.amount
        todo.owner_id = userId
        
        try:
            db.add(todo)
            db.commit()
        except:
            return {'status': False, 'message': "Unsuccessfully!"}
        
        return {'status': True, 'message': "Successfully"}
    except:
        return {'status': False, 'message': "CatchError"}

@router.get('/get-all-todos', response_class=JSONResponse)
async def getAllAllTodos(request: Request, db: Session = Depends(get_db)):
    try:
        userId = request.state.user["id"]

        todos = (db.query(models.Todos).filter(models.Todos.owner_id == userId).order_by(models.Todos.id).all())
    except:
        return {'status': False, 'message': "Unsuccessfully!"}
    
    return {'status': True, 'message': "Successfully!", 'data': todos }

@router.get('/get-by-id-todo/{todo_id}', response_class=JSONResponse)
async def getByIdTodo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = (db.query(models.Todos).filter(models.Todos.id == todo_id).first())
    except:
        return {'status': False, 'message': "Unsuccessfully!"}
    
    return {'status': True, 'message': "Successfully!", 'data': todo }

@router.put('/update-todo', response_class=JSONResponse)
async def updateTodo(request: Request, updateTodo: dto.UpdateTodo, db: Session = Depends(get_db)):
    try:
        userId = request.state.user["id"]
        
        try:
            (db.query(models.Todos).filter(models.Todos.id == updateTodo.id)
             .filter(models.Todos.owner_id == userId)
             .update({"title": updateTodo.title, "description": updateTodo.description, 
                        "amount": updateTodo.amount, "is_completed": updateTodo.is_completed}))
            db.commit()
        except:
            return {'status': False, 'message': "Unsuccessfully!"}
        
        return {'status': True, 'message': "Successfully"}
    except:
        return {'status': False, 'message': "CatchError"}

@router.put('/update-todo-status', response_class=JSONResponse)
async def updateTodoStatus(request: Request, updateTodoStatus: dto.UpdateTodoStatus, db: Session = Depends(get_db)):
    try:
        userId = request.state.user["id"]
        
        try:
            (db.query(models.Todos).filter(models.Todos.id == updateTodoStatus.id)
             .filter(models.Todos.owner_id == userId)
             .update({"is_completed": updateTodoStatus.is_completed}))
            db.commit()
        except:
            return {'status': False, 'message': "Unsuccessfully!"}
        
        return {'status': True, 'message': "Successfully"}
    except:
        return {'status': False, 'message': "CatchError"}

@router.delete('/delete-todo', response_class=JSONResponse)
async def deleteTodo(request: Request, deleteTodo: dto.DeleteTodo, db: Session = Depends(get_db)):
    try:
        userId = request.state.user["id"]

        try:
            db.query(models.Todos).filter(models.Todos.id == deleteTodo.id and models.Todos.owner_id == userId).delete()
            db.commit()
        except:
            return {'status': False, 'message': "Unsuccessfully!"}
        
        return {'status': True, 'message': "Successfully"}
    except:
        return {'status': False, 'message': "CatchError"}
