import secrets

from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from starlette.routing import Route
from pydantic import BaseModel
from hashlib import sha256



app = FastAPI()
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62502553'
app.counter = 0
app.sessions = []

users = []

templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

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

def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(credentials.username, "trudnY")
	correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
	if not (correct_username and correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	else:
		users.clear()
		users.append(credentials.username)
		session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding = 'utf8')).hexdigest()
		app.sessions.clear()
		app.sessions.append(session_token)
		return session_token 

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    return RedirectResponse(url='/welcome') 

@app.post('/logout')
def wylogowanie(response: Response):
	if len(app.sessions)!=1:
		pass
	else:
		session_token = app.sessions[0]
		response.delete_cookie(key="session_token")
		app.sessions.clear()
		users.clear()
		print("wylogowano")
	return RedirectResponse(url='/')

