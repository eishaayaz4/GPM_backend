from sqlalchemy.orm import relationship
from  dbHandler import DBHandler
from models import User
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Date
class History(DBHandler.Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String(100))
    date = Column(Date)
    user_id = Column(Integer, ForeignKey('User.id'))
    description = Column(String(100))
    # Define the relationship to the User table
    user = relationship("User", back_populates="histories")



