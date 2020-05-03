from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic import BaseModel

from hashlib import sha256

import secrets
import sqlite3


app = FastAPI()
security = HTTPBasic()

app.counter = 0
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62506553'
patients = []
app.sessions = []
app.users = []


class HelloResp(BaseModel):
    msg: str

class Patient(BaseModel):
    name: str
    surename: str

class PatientID(BaseModel):
    id: int
    patient: Patient

# ------------------------------------------------------

def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    user, passw = credentials.username, credentials.password
    correct_username = secrets.compare_digest(user, "trudnY")
    correct_password = secrets.compare_digest(passw, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        session_token = sha256(bytes(f"{user}{passw}{app.secret_key}", encoding = 'utf8')).hexdigest()
        if not (session_token in app.sessions):
            app.sessions.append(session_token)
            app.users.append(user)
        return session_token 

# ------------------------------------------------------  

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = '/welcome'

@app.post('/logout')
def logout(response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        return RedirectResponse(url='/')
    response.delete_cookie(key='cookie')
    app.sessions.clear()
    return RedirectResponse(url='/')

@app.post('/')
@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}
    
@app.get('/welcome')
def welcome(request: Request, response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    user = app.users[0]
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    return HelloResp(msg=f"Hello {name}")


@app.post('/patient', response_model=PatientID)
def add_patient(request: Patient, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    global patients
    p = PatientID(id = app.counter, patient = request)
    app.counter+=1
    patients.append(p)
    return p

@app.get('/patient/{pk}')
def read_patient(pk: int, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    global patients
    if pk not in [i.id for i in patients]:
       return JSONResponse(status_code = 204, content = {}) 
    return patients[pk].patient



@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()
    
@app.get('/tracks/')
async def read_tracks(page: int = Query(0), per_page: int = Query(10)): 
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute(
		"SELECT * FROM tracks ORDER BY TrackId").fetchall()
	current_tracks = data[per_page*page:per_page*(page+1)]
	return current_tracks

@app.get('/tracks/composers')
async def read_composers(composer_name: str = Query(None)):
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute(
		"SELECT Name FROM tracks WHERE Composer= :composer_name ORDER BY Name",
		{'composer_name': composer_name}).fetchall()

	traki = []
	for elem in data:
		traki.append(elem["Name"])

	if len(data)==0:
		raise HTTPException(
			status_code=404,
			detail= {"error": "Composer not in database"}
		)

	return traki

class Album(BaseModel):
    title: str
    artist_id: int

@app.post('/albums', status_code=201)
async def albums(request: Album):
    cursor = await app.db_connection.execute(f'''
    SELECT COUNT(*) FROM artists WHERE artists.ArtistId = {request.artist_id}''')
    existance = await cursor.fetchone()
    if (existance[0] == 0):
        raise HTTPException(detail={"error": f"Artysta o numerze {request.artist_id} nie istnieje"},
                            status_code=status.HTTP_404_NOT_FOUND)

    cursor = await app.db_connection.execute(f'''
    INSERT INTO albums (Title, ArtistId) VALUES("{request.title}", {request.artist_id});''')
    await app.db_connection.commit()

    cursor = await app.db_connection.execute(f'''
    SELECT AlbumId FROM albums WHERE Albums.Title = "{request.title}" ORDER BY AlbumId DESC LIMIT 1;''')
    albums = await cursor.fetchone()
    AlbumId = albums[0]
    return {
            "AlbumId": AlbumId,
            "Title": request.title,
            "ArtistId": request.artist_id
            }
