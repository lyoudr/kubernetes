from fastapi import FastAPI 
import requests

app = FastAPI() 


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
    res = requests.get('/sales')
    return res

    