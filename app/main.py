from fastapi import FastAPI
from app.database import Base,engine
import app.models,app.schemas,app.crypto,app.services
from app.routers import auth,keys,messages,ws,safety
from app.services import ensure_bucket_exists
app = FastAPI(title='Fortrx')
app.include_router(keys.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(ws.router)
app.include_router(safety.router)
#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
ensure_bucket_exists()
@app.get('/')
def health():
    return {"status":"Fortrx is running"}


# docker run -d --name localstack -p 4566:4566 localstack/localstack
# docker run -p 6379:6379 redis:alpine