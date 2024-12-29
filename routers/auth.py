import sys
import models
import dto

from fastapi import Depends, APIRouter, Request
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy.exc import IntegrityError
from database import engine, SessionLocal
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import timedelta
from configData import ConfigData
from helper import Helper

sys.path.append('..')

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'user': 'Not authorized'
        }
    }
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post('/user-register')
async def userRegister(request: Request, userRegister: dto.UserRegister, db: Session = Depends(get_db)):
    user = models.Users()
    user.email = userRegister.email
    user.username = userRegister.username
    user.is_active = False

    userInfo = db.query(models.Users).filter(models.Users.email == user.email).first()

    if userInfo is None or not userInfo.is_active:
        hashedPassword = Helper.get_password_hash(userRegister.password)
        if hashedPassword is not None:
            user.password = hashedPassword
        else:
            return {'status': False, 'message': "Parolynyz tazeden yazyn!"}
        
        if userInfo is None:
            try:
                db.add(user)
                db.commit()
                db.refresh(user)
            except IntegrityError:
                return {'status': False, 'message': "IntegrityError!"}
            except:
                return {'status': False, 'message': "Unsuccessfully!"}
        
        checkRegisterTokenExpires = timedelta(minutes=ConfigData.CHECK_REGISTER_TOKEN_EXPIRE_MINUTES)
        checkRegisterToken = Helper.create_access_token(
            data={"id": user.id, "username": userRegister.username, 'email': userRegister.email, 'password': userRegister.password},
            expires_delta = checkRegisterTokenExpires, 
            secreteKeyRegister = ConfigData.SECRET_KEY_REGISTER)

        return {'status': True, 'message': "Hasaba alys ustinlikli! email e barmaly token: "+checkRegisterToken, }
    else:
        return {'status': False, 'message': "Bu email hasaba alynan. Giris yapin!"}

@router.post('/user-register-check')
async def userRegisterCheck(request: Request, userRegisterCheck: dto.UserRegisterCheck, db: Session = Depends(get_db)):
    try:
        user = models.Users()
        token = userRegisterCheck.token

        if token is None:
            return {'status': False, 'message': "UNAUTHORIZED. Rugsadynyz yok!", "status_code": status.HTTP_401_UNAUTHORIZED}
        
        payload = jwt.decode(token, ConfigData.SECRET_KEY_REGISTER, algorithms=[ConfigData.ALGORITHM])

        user.email = payload.get("email")
        user.username = payload.get("username")
        user.password = payload.get("password")
        user.id = payload.get("id")

        if user.email is not None:
            userInfo = db.query(models.Users).filter(models.Users.email == user.email).first()
            db.query(models.Users).filter(models.Users.email == user.email).update({"is_active": True})
            db.commit()

            accessTokenExpires = timedelta(minutes=ConfigData.ACCESS_TOKEN_EXPIRE_MINUTES)
            accessToken = Helper.create_access_token(
                data={"id": userInfo.id, 'email': userInfo.email},
                expires_delta = accessTokenExpires, 
                secreteKeyRegister = ConfigData.SECRET_KEY_LOGIN)

            return {'status': True, 'message': "Hasaba alys ustinlikli! AccessToken: "+accessToken, }
        else:
            return {'status': False, 'message': "Dogry token dal!"}

    except ExpiredSignatureError:
        return {'status': False, 'message': "Tassyklama wagtynyz doldy tazeden synansyn!"}
    except JWTError:
        return {'status': False, 'message': "UNAUTHORIZED. Rugsadynyz yok!", "status_code": status.HTTP_401_UNAUTHORIZED}
    
@router.post('/user-login')
async def userLogin(request: Request, userLogin: dto.UserLogin, db: Session = Depends(get_db)):
    email = userLogin.email
    password = userLogin.password

    if email is None or password is None:
        return {'status': False, 'message': "Emailnizy ve acar sozuniz  girizin!"}
    
    userInfo = db.query(models.Users).filter(models.Users.email == email).first()
    
    if userInfo is None:
        return {'status': False, 'message': "Hasaba alynmadyk. Hasap doredin!"}
    
    if not Helper.verify_password(password, userInfo.password):
        return {'status': False, 'message': "Acar sozuniz yalnys!", }
    
    accessTokenExpires = timedelta(minutes=ConfigData.ACCESS_TOKEN_EXPIRE_MINUTES)
    accessToken = Helper.create_access_token(
        data={"id": userInfo.id, 'email': userInfo.email},
        expires_delta = accessTokenExpires, 
        secreteKeyRegister = ConfigData.SECRET_KEY_LOGIN)

    return {'status': True, 'message': "Successfull!", "access_token": accessToken }
