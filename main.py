from database import *
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Product(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    
class Order(BaseModel):
    id: int
    quantity: int

class MessageResponse(BaseModel):
    message: str
    
class OrderStatus(BaseModel):
    status: Literal["в процессе", "отправлен", "доставлен"]
    
def create_product(db: Session, product: Product):
    db_product = ProductDB(name = product.name,
                           description = product.description,
                           price = product.price,
                           quantity = product.quantity)
    first = db.query(ProductDB).filter(ProductDB.name == db_product.name).first()
    if first:
        raise HTTPException(status_code=400, detail="Продукт уже создан")
    else:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
    return {'id': db_product.id, "message": "Продукт успешно создан"}

def delete_product(db: Session, product_id: int):
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    db.delete(db_product)
    db.commit()
    return {"message": "Продукт успешно удален"}

def edit_product(db: Session, id: int, product: Product):
    id_product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if id_product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    id_product.name = product.name
    id_product.description = product.description
    id_product.price = product.price
    id_product.quantity = product.quantity
    db.commit()
    db.refresh(id_product)
    return {'id': id_product.id, "message": "Продукт успешно удален"}
    
def create_order(db: Session, order: Order):
    product = db.query(ProductDB).filter(ProductDB.id == order.id).first()  
    if product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    if order.quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Не достаточно товара на складе")
    new_order = OrderDB(status = 'В процессе')
    product.quantity = product.quantity - order.quantity
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    db.refresh(product)
    order_item = OrderitemDB(order_id = new_order.id,
                             product_id = product.id,
                             quantity = order.quantity)
    db.add(order_item)
    db.commit()
    return {'id': product.id, "message": "Заказ успешно создан"}

def order_status(db: Session, id: int,  orderstatus: OrderStatus):
    id_order = db.query(OrderDB).filter(OrderDB.id == id).first()
    if id_order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    id_order.status = orderstatus.status
    db.commit()
    db.refresh(id_order)
    return {'id': id_order, "message": "Статус обновлен"}

app = FastAPI()

@app.post('/products')
def create_new_products(product: Product, db: Session = Depends(get_db)):
    return create_product(db, product)

@app.get('/products')
def all_product():
    all_product = db.query(ProductDB).all()
    return all_product

@app.get('/products/{id}')
def id_product(id: int, db: Session = Depends(get_db)):
    idproduct = db.query(ProductDB).filter(ProductDB.id == id).first()
    if idproduct is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return idproduct

@app.put('/product/{id}')
def edit_products(id: int, product: Product, db: Session = Depends(get_db)):
    return edit_product(db, id, product)
    
@app.delete('/products/{id}')
def delete_products(id: int, db: Session = Depends(get_db)):
    return delete_product(db, id)

@app.post('/orders')
def create_new_order(order: Order, db: Session = Depends(get_db)):
    return create_order(db, order)

@app.get('/orders')
def all_orders():
    allorders = db.query(OrderDB).all()
    return allorders

@app.get('/orders/{id}')
def id_order(id: int, db: Session = Depends(get_db)):
    idorder = db.query(OrderitemDB).filter(OrderitemDB.id == id).first()
    order = db.query(OrderDB).filter(OrderDB.id == id).first()
    if idorder is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return idorder, order.status

@app.patch('/orders/{id}/status')
def orders_status(id:int, orderstatus: OrderStatus, db: Session = Depends(get_db)):
    return order_status(db, id, orderstatus)

@app.get("/")
async def read_root():
    return {"Hello": "World"}