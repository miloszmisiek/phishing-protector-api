from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class UrlsData(BaseModel):
    urls: List[str] = Field(..., description="A list of URLs to process")

    class Config:
        schema_extra = {
            "example": {
                "urls": ["https://www.google.com", "https://www.twitter.com", "https://www.facebook.com"]
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
