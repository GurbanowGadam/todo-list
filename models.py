from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Double
from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    username = Column(String(200), unique=True, index=True, nullable=False)
    password = Column(String(225), nullable=False)
    is_active = Column(Boolean, default=False)

    todos = relationship('Todos', back_populates='owner')


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(225), nullable=False)
    description = Column(String(225))
    amount = Column(Double)
    is_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship('Users', back_populates='todos')