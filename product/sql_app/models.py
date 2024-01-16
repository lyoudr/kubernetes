from sqlalchemy import Boolean, Column, String, Integer 
from .database import Base 

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    