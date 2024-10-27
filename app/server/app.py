from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.server.routes.urls import router as UrlsRouter
from app.server.routes.auth import router as AuthRouter

origins = ['https://x.com', 'https://twitter.com',
           'chrome-extension://gefeonighpcjgmdlhanednlikmdabpfg', 'chrome-extension://kkmfcnoeffmmfiplcjmfciphjkibfekg']

logging.basicConfig(level=logging.DEBUG, filename='app.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UrlsRouter, tags=["Urls"])
app.include_router(AuthRouter, tags=["Auth"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Phishing Protector API!"}
