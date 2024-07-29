from sql_app import crud, database, models 

from cachetools import TTLCache
from sqlalchemy.orm import Session 
from fastapi import FastAPI, Depends 
from google.cloud import storage 
import requests
import json
import csv 

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI() 

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db 
    finally:
        db.close()

# Create a cache with a  TTL (Time-to-Live) of 300 seconds 
cache = TTLCache(maxsize = 100, ttl=300)

# Dependency to get an item from the database with caching 
def get_item_with_cache(item_id: int, db: Session = Depends(get_db)):
    cached_item = cache.get(item_id)
    if cached_item:
        return cached_item
    

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

@app.post('/product/create_file')
def create_file():
    data = {
        'Name': ['John', 'Alice', 'Bob'],
        'Age': [25, 30, 22],
        'City': ['New York', 'San Francisco', 'Seattle']
    }
    csv_file = '/cache/output.csv'
    # Writing to CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        # Creating a CSV writer object
        csv_writer = csv.writer(csvfile)
        # Writing the header
        csv_writer.writerow(data.keys())
        # Writing the data
        for row in zip(*data.values()):
            csv_writer.writerow(row)
    upload_file('/cache/output.csv')

def upload_file(local_path:str):
    client = storage.Client() 
    bucket = client.bucket('test_kd')
    blob = bucket.blob('csv/output.csv')
    blob.upload_from_filename(local_path)