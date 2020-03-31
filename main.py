from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def Hello_World():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
def method1(request: Request):
    used_method=request.method
    return {"method": used_method}

@app.post("/method")
def method2(request: Request):
    used_method=request.method
    return {"method": used_method}
