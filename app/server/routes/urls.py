from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from app.server.database import (
    predict_model,
    add_to_whitelist,
    add_to_blacklist
)
from app.server.models.urls import (
    ErrorResponseModel,
    ResponseModel,
    UrlsData
)

router = APIRouter()


@router.post("/predict", response_description="")
async def predict(data: UrlsData = Body(...)):
    data = jsonable_encoder(data)
    data = data['urls']
    new_predictions = await predict_model(data)
    if new_predictions:
        return ResponseModel(new_predictions, "Predictions run successfully.")
    return ErrorResponseModel("An error occurred.", 404, "No predictions found.")


@router.post("/add-to-whitelist", response_description="")
async def add_to_whitelist_route(data: UrlsData = Body(...)):
    data = jsonable_encoder(data)
    data = data['urls']
    new_whitelist = await add_to_whitelist(data)
    if new_whitelist:
        return ResponseModel(new_whitelist, "URLs added to whitelist successfully.")
    return ErrorResponseModel("An error occurred.", 404, "URLs not added to whitelist.")


@router.post("/add-to-blacklist", response_description="")
async def add_to_blacklist_route(data: UrlsData = Body(...)):
    data = jsonable_encoder(data)
    data = data['urls']
    new_blacklist = await add_to_blacklist(data)
    if new_blacklist:
        return ResponseModel(new_blacklist, "URLs added to blacklist successfully.")
    return ErrorResponseModel("An error occurred.", 404, "URLs not added to blacklist.")
