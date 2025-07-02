import os
from contextlib import asynccontextmanager
from typing import Literal

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, status
from pydantic import BaseModel

load_dotenv()

DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
DEEPAI_API_URL = "https://api.deepai.org/api/nsfw-detector"
NSFW_THRESHOLD = 0.7


class ModerationOKResponse(BaseModel):
    status: Literal["OK"]


class ModerationRejectedResponse(BaseModel):
    status: Literal["REJECTED"]
    reason: Literal["NSFW content"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_session = aiohttp.ClientSession()
    yield
    await app.state.http_session.close()


app = FastAPI(lifespan=lifespan)


@app.post(
    "/moderate", response_model=ModerationOKResponse | ModerationRejectedResponse, summary="Модерация изображения"
)
async def moderate_image(file: UploadFile):
    # Validate file extension
    if not file.filename.lower().endswith((".jpg", ".png")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Разрешены только изображения форматов .jpg и .png"
        )

    content = await file.read()

    try:
        async with app.state.http_session.post(
            DEEPAI_API_URL, data={"image": content}, headers={"api-key": DEEPAI_API_KEY}
        ) as response:
            if response.status != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY, detail="Не удалось получить ответ от DeepAI API"
                )

            result = await response.json()
            nsfw_score = result.get("output", {}).get("nsfw_score", 0)

            if nsfw_score > NSFW_THRESHOLD:
                return {"status": "REJECTED", "reason": "NSFW content"}
            return {"status": "OK"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при обработке изображения: {str(e)}"
        ) from None
