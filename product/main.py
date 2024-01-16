from sql_app import crud, database, models 

from sqlalchemy.orm import Session 
from fastapi import FastAPI, Depends 
import requests
import json

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI() 

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db 
    finally:
        db.close()

@app.get('/')
def read_root():
    return {"message": "Hello World!"}

@app.get('/product')
def get_sales():
    return {"message": "ok"}

@app.get('/product/aaa')
def get_sales():
    return {"message": "ok"}

@app.get('/product/bbb')
def get_sales():
    # res = requests.get('http://10.107.0.50/sales') # Because pod IP may change
    res = requests.get('http://sales-service/sales') # Instead, use service name
    return res.json()

@app.get('/product/item')
def get_product(
    db: Session = Depends(get_db),
):
    res = crud.get_product(db, 1)
    return res

    