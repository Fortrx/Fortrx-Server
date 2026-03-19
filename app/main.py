from fastapi import FastAPI
from app.database import Base,engine
import app.models,app.schemas,app.crypto,app.services
from app.routers import auth
app = FastAPI(title='Fortress')
#Base.metadata.drop_all(bind=engine)
app.include_router(auth.router)
Base.metadata.create_all(bind=engine)
@app.get('/')
def health():
    return {"status":"Fortress is running"}