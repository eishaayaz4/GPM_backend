from sqlalchemy.orm import relationship
from  dbHandler import DBHandler
from sqlalchemy import Column, Integer, String, ForeignKey,CHAR
from sqlalchemy.orm import relationship
class Asset(DBHandler.Base):
    __tablename__ = 'Asset'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    image = Column(String(100))
    isAsset = Column(CHAR(1))
    drafts = relationship("Draft", back_populates="asset")
    user = relationship("User", back_populates="asset")