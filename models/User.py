from sqlalchemy.orm import relationship
from models import History
from  dbHandler import DBHandler
from  sqlalchemy import Column,Integer,String

class User(DBHandler.Base):
    __tablename__='User'
    id=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(String(100))
    email=Column(String(100))
    password=Column(String(100))
    role=Column(String(100))
    histories = relationship("History", back_populates="user")
    asset = relationship("Asset", back_populates="user")
    drafts = relationship("Draft", back_populates="user")
