from fastapi import FastAPI 

app = FastAPI() 

@app.get('/healthz')
def read_root():
    return {"message": "Healthy"}

@app.get('/sales/livez')
def liveness():
    return {"message": "alive"}

@app.get('/sales')
def get_sales():
    return {"message": "This is sales one"}