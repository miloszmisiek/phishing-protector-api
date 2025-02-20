from fastapi import APIRouter, Body, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from io import StringIO
import pandas as pd
from app.services.logger import logger
import os
from datetime import datetime

from app.server.classification import (
    predict_model,
    add_to_whitelist,
    add_to_blacklist,
    url_features
)
from app.server.models.urls import (
    ErrorResponseModel,
    ResponseModel,
    UrlsData
)

router = APIRouter()

@router.post("/predict-from-csv", response_description="Upload a CSV file for predictions")
async def predict_from_csv(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")

        # Read the uploaded CSV file
        content = await file.read()
        logger.debug(f"File content read successfully, size: {len(content)} bytes")

        # Decode and load into a DataFrame
        df = pd.read_csv(StringIO(content.decode("utf-8")))
        logger.info(f"CSV loaded into DataFrame with columns: {list(df.columns)}")

        # Ensure required columns exist
        if "urls" not in df.columns or "labels" not in df.columns:
            logger.error("Missing required columns in CSV: 'urls' and 'labels'")
            return ErrorResponseModel(
                "Invalid CSV format", 400, "CSV must have 'urls' and 'labels' columns."
            )
        
        # Extract URLs and labels
        urls = df["urls"].tolist()
        labels = df["labels"].tolist()
        logger.info(f"Extracted {len(urls)} URLs and labels from CSV")

        # Get predictions
        predictions = await predict_model(urls)
        logger.info(f"Predictions generated: {predictions}")
        logger

        # Compare predictions with labels
        results = []
        correct_predictions = 0
        for url, label, prediction in zip(urls, labels, predictions):
            prediction = predictions.get(url)
            is_correct = label == round(prediction)
            if is_correct:
                correct_predictions += 1

            result = {
                "url": url,
                "label": label,
                "prediction": prediction,
                "is_correct": is_correct
            }
            results.append(result)  # Append the result dictionary directly to the results list
            logger.debug(f"Processed result: {result}")

        accuracy = (correct_predictions / len(labels)) * 100 if labels else 0
        logger.info(f"Prediction accuracy: {accuracy:.2f}%")

        logger.info(f"Total results processed: {len(results)}")
        return ResponseModel({"results": results, "accuracy": accuracy}, "Predictions compared to labels successfully.")

    except Exception as e:
        logger.exception("An error occurred during processing")
        return ErrorResponseModel("An error occurred.", 500, str(e))
    

@router.post("/features-from-csv", response_description="Upload a CSV file for feature extraction")
async def features_from_csv(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")

        # Read the uploaded CSV file
        content = await file.read()
        logger.debug(f"File content read successfully, size: {len(content)} bytes")

        # Decode and load into a DataFrame
        input_df = pd.read_csv(StringIO(content.decode("utf-8")))
        logger.info(f"CSV loaded into DataFrame with columns: {list(input_df.columns)}")

        # Ensure required column exists
        if "urls" not in input_df.columns:
            logger.error("Missing required column in CSV: 'urls'")
            return ErrorResponseModel(
                "Invalid CSV format", 400, "CSV must have 'urls' column."
            )
        
        # Extract URLs
        urls = input_df["urls"].tolist()
        logger.info(f"Extracted {len(urls)} URLs from CSV")

        # Get features
        features = await url_features(urls)
        logger.info(f"Features extracted for {len(features)} URLs")

        # Convert features to DataFrame and sort columns alphabetically
        features_df = pd.DataFrame(features)
        features_df = features_df.reindex(sorted(features_df.columns), axis=1)
        
        # Move 'url' column to the end
        cols = list(features_df.columns)
        cols.remove('url')
        cols.append('url')
        features_df = features_df[cols]
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"extracted_features_{timestamp}.csv"
        output_path = f"app/data/features/{output_filename}"
        
        # Ensure directory exists
        os.makedirs("app/data/features", exist_ok=True)
        
        # Save to CSV without index
        features_df.to_csv(output_path, index=False)
        logger.info(f"Features saved to {output_path}")

        # Return the file as response
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )

    except Exception as e:
        logger.exception("An error occurred during processing")
        return ErrorResponseModel("An error occurred.", 500, str(e))


@router.post("/predict", response_description="")
async def predict(data: UrlsData = Body(...)):
    data = jsonable_encoder(data)
    data = data['urls']
    new_predictions = await predict_model(data)
    return ResponseModel(new_predictions, "Predictions run successfully.") if new_predictions else ErrorResponseModel("An error occurred.", 404, "No predictions found.")

@router.post("/url-features", response_description="")
async def url_features_route(data: UrlsData = Body(...)):
    data = jsonable_encoder(data)
    data = data['urls']
    new_features = await url_features(data)
    return ResponseModel(new_features, "Features extracted successfully.") if new_features else ErrorResponseModel("An error occurred.", 404, "Features not extracted.")


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
