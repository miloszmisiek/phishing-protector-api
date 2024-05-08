from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.server.routes.urls import router as UrlsRouter

origins = ['https://twitter.com',
           'chrome-extension://gefeonighpcjgmdlhanednlikmdabpfg']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UrlsRouter, tags=["Urls"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Phishing Protector API!"}
