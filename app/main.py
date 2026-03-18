from fastapi import FastAPI
from app.database import Base,engine
import app.models
app = FastAPI(title='Fortress')
#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
@app.get('/')
def health():
    return {"status":"Fortress is running"}