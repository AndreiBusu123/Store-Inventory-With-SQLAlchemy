from sqlalchemy import (create_engine, Column, Integer, String, ForeignKey, Date)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# define the db and session
engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# create the Product model
class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    product_quantity = Column(Integer, nullable=False)
    product_price = Column(Integer, nullable=False)
    date_updated = Column(Date, nullable=False)

# this was used for testing when I needed printouts. 
    def __repr__(self):
        return f"<Product(product_id={self.product_id}, product_name='{self.product_name}', product_quantity={self.product_quantity}, product_price={self.product_price}, date_updated='{self.date_updated}')>"
  

