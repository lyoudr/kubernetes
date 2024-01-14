from fastapi import FastAPI 
import requests

app = FastAPI() 


@app.get('/')
def read_root():
    return {"message": "Hello World!"}

@app.get('/get_sales')
def get_sales():
    res = requests.get('http://sales-service/sales')
    return res 


    