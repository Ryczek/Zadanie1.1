from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
app.counter = 0
global patients
patients = []


class HelloResp(BaseModel):
    msg: str

@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")

@app.get("/")
def Hello_World():
    return {"message": "Hello world!"}

@app.get("/welcome")
def Hello_World():
    return {"message": "Hello world!"}

@app.get("/method")
def method(request: Request):
    used_method=request.method
    return {"method": used_method}

@app.post("/method")
def method(request: Request):
    used_method=request.method
    return {"method": used_method}

@app.put("/method")
def method(request: Request):
    used_method=request.method
    return {"method": used_method}

class Patient(BaseModel):
    name: str
    surename: str


class PatientID(BaseModel):
    id: int
    patient: Patient 


@app.post('/patient', response_model=PatientID)
def add_patient(request: Patient):

    p = PatientID(id = app.counter, patient = request)
    app.counter+=1
    patients.append(p)
    return p

@app.get('/patient/{pk}')
def read_patient(pk: int):

    if pk not in [i.id for i in patients]:
       return JSONResponse(status_code = 204, content = {}) 
    return patients[pk].patient

