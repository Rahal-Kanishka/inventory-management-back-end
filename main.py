from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from routes import orderRoute, ingredientRoute, batchRoute, locationRoute, recipeRoute, grnRoute, productRoute
from routes import userRoute
from utils.database import engine
from models import models
import logging
logging.basicConfig(level=logging.DEBUG)



app = FastAPI(title="Group5")
#app.include_router(receipyRoute.router)
app.include_router(ingredientRoute.router)
app.include_router(userRoute.router)
app.include_router(orderRoute.router)

app.include_router(batchRoute.router)

app.include_router(locationRoute.router)

app.include_router(recipeRoute.router)

app.include_router(grnRoute.router)

app.include_router(productRoute.router)

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.middleware("http")
# async def exception_handling(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as exc:
#         return JSONResponse(status_code=500, content='Error occurred: {}'.format(exc))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def root():
    return "Pong"
