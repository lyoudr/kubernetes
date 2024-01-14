from fastapi import FastAPI 

app = FastAPI() 

@app.get('/')
def read_root():
    return {"message": "Healthy"}

@app.get('/livez')
def liveness():
    return {"message": "alive"}

@app.get('/sales')
def get_sales():
    return {"message": "This is sales one"}