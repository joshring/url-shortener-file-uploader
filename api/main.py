from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database.document_db import dynamodb_lifespan
from apis.urls import urls_api
from http import HTTPStatus
from mangum import Mangum
from environment.env import frontend_url, in_lambda_fn
import logging

logger = logging.getLogger("__name__")

app = FastAPI(lifespan=dynamodb_lifespan)

origins = []
if in_lambda_fn:
    origins = f"{frontend_url}/"

else:
    origins = [
        "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "date",
        "keep-alive",
        "Content-Type",
        "Authorization",
        "Origin",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Headers",
    ],
    expose_headers=[
        "date",
        "keep-alive",
        "Origin",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Headers",
    ],
)

app.include_router(urls_api)


@app.exception_handler(RequestValidationError)
async def fastapi_bad_requests(request: Request, exc: RequestValidationError):
    """
    Convert HTTP 422 errors to more standard HTTP bad request 400
    """
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={"detail": exc.errors()},
    )


lambda_handler = Mangum(app, lifespan="on")
