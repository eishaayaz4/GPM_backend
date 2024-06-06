from sqlalchemy.orm import relationship
from  dbHandler import DBHandler
from sqlalchemy import Column, Integer, String, ForeignKey,Float
from sqlalchemy import Date
class Draft(DBHandler.Base):
    __tablename__ = 'Draft'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    group_image = Column(String(100))
    individual_image = Column(String(100))
    x=Column(Float)
    y= Column(Float)
    height = Column(Float)
    width = Column(Float)
    actual_height = Column(Float)
    actual_width = Column(Float)
    date = Column(Date)
    module=Column(String(100))
    current_screen=Column(String(100))
    user = relationship("User", back_populates="drafts")

