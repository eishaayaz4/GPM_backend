from  dbHandler import DBHandler
from  sqlalchemy import Column,Integer,String

class Template(DBHandler.Base):
    __tablename__='Template'
    id=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(String(100))
    type=Column(String(100))
    category=Column(String(100))
    image=Column(String(100))