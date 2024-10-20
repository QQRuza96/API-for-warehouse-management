from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from datetime import datetime, timezone

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={'check_same_thread' : False})

class Base(DeclarativeBase): pass
class ProductDB(Base):    
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    
    order_items = relationship('OrderitemDB', back_populates='product')
    
class OrderDB(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String)
    
    items = relationship('OrderitemDB', back_populates='order')
    
class OrderitemDB(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    
    order = relationship('OrderDB', back_populates='items')
    product = relationship('ProductDB', back_populates='order_items')

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()