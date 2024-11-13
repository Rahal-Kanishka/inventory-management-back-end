from fastapi import FastAPI, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routes import orderRoute, ingredientRoute, batchRoute, locationRoute, recipeRoute, grnRoute
from routes import userRoute
from utils.database import engine
from models import models




app = FastAPI(title="Group5")
#app.include_router(receipyRoute.router)
app.include_router(ingredientRoute.router)
app.include_router(userRoute.router)
app.include_router(orderRoute.router)

app.include_router(batchRoute.router)

app.include_router(locationRoute.router)

app.include_router(recipeRoute.router)

app.include_router(grnRoute.router)

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def root():
    return "Pong"
