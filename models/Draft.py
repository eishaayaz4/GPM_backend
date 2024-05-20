from sqlalchemy.orm import relationship
from  dbHandler import DBHandler
from models import Asset
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Date
class Draft(DBHandler.Base):
    __tablename__ = 'Draft'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    asset_id = Column(Integer, ForeignKey('Asset.id'))
    image = Column(String(100))
    asset = relationship("Asset", back_populates="drafts")

