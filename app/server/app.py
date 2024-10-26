from fastapi import FastAPI
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.server.routes.urls import router as UrlsRouter
from passlib.context import CryptContext
from jose import JWTError, jwt

origins = ['https://x.com', 'https://twitter.com',
           'chrome-extension://gefeonighpcjgmdlhanednlikmdabpfg', 'chrome-extension://kkmfcnoeffmmfiplcjmfciphjkibfekg']

logging.basicConfig(level=logging.DEBUG, filename='app.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
