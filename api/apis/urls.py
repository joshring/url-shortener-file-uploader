from typing import Annotated, Any
import random
from string import ascii_lowercase
import logging
import io

from fastapi import (
    Body,
    Depends,
    Path,
    File,
    APIRouter,
    HTTPException,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from http import HTTPStatus

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import boto3

from environment.env import s3_bucket_name, s3_bucket_https_url, server_host

from database.document_db import dynamodb_conn
from models.models import (
    UrlType,
    UserUrls,
    Url,
    UrlInDB,
    UrlRequest,
)

logger = logging.getLogger(__name__)


urls_api = APIRouter(
    tags=["urls"],
)


def s3upload(
    s3_bucket_name: str,
    filedata: File,
    s3_key: str,
):
    s3_client = boto3.client(service_name="s3")
    try:
        s3_client.upload_fileobj(filedata, s3_bucket_name, s3_key)

    except ClientError as err:
        logger.error(
            f"Couldn't upload to s3 bucket: {s3_bucket_name}. Here's why: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}"
        )
        raise HTTPException(HTTPStatus.BAD_REQUEST, err.response["Error"]["Message"])


def gen_url_store_in_dynamo(
    dynamodb,
    original_url: str,
    username: str,
    url_type: UrlType,
) -> Url:

    random_str = "".join([random.choice(ascii_lowercase) for _ in range(12)])
    short_url = f"{server_host}/{random_str}"

    new_url = UrlInDB(
        original_url=original_url,
        url_type=url_type,
        short_url=short_url,
        user_name=username,
    )

    urls_table = dynamodb.Table("urls")

    try:
        urls_table.put_item(Item=new_url.model_dump())

    except ClientError as err:
        logger.error(
            f"Couldn't put_item into urls table. Here's why: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}"
        )
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, err.response["Error"]["Message"])

    return Url(**new_url.model_dump())


@urls_api.post("/files/{filename}")
async def post_file(
    filename: Annotated[str, Path()],
    dynamodb: Annotated[Any, Depends(dynamodb_conn)],
    file: UploadFile = File(),
):

    # Convert to bytes and pass to S3 upload
    upload_file = io.BytesIO(await file.read())

    s3upload(
        s3_bucket_name,
        upload_file,
        filename,
    )

    original_url = f"https://{s3_bucket_https_url}/{filename}"

    return gen_url_store_in_dynamo(
        dynamodb=dynamodb,
        username="hard_coded_user",
        original_url=original_url,
        url_type=UrlType.file_url,
    )


@urls_api.post("/urls")
async def post_url(
    create_url: Annotated[UrlRequest, Body()],
    dynamodb: Annotated[Any, Depends(dynamodb_conn)],
) -> Url:

    return gen_url_store_in_dynamo(
        dynamodb=dynamodb,
        username="hard_coded_user",
        original_url=create_url.original_url,
        url_type=UrlType.site_url,
    )


@urls_api.get("/urls")
async def get_urls(
    dynamodb: Annotated[Any, Depends(dynamodb_conn)],
) -> UserUrls:

    urls_table = dynamodb.Table("urls")

    try:
        response = urls_table.scan(
            FilterExpression=Attr("user_name").eq("hard_coded_user"),
        )

    except ClientError as err:
        logger.error(
            f"Couldn't scan urls table for user_name {"hard_coded_user"}. Here's why: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}"
        )
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, err.response["Error"]["Message"])

    if response.get("Items") is None:
        return UserUrls(
            user_name="hard_coded_user",
            urls=[],
        )

    list_urls = []

    for item in response.get("Items"):
        list_urls.append(Url(**item))

    return UserUrls(
        user_name="hard_coded_user",
        urls=list_urls,
    )


@urls_api.get("/{short_url:path}")
async def get_url_redirect(
    dynamodb: Annotated[Any, Depends(dynamodb_conn)],
    short_url: Annotated[str, Path()],
) -> RedirectResponse:
    """
    Redirecting the short_url to the original_url found by lookup
    """

    urls_table = dynamodb.Table("urls")

    # Append API's host to the URL to search in the DB
    short_url_in_db = f"{server_host}/{short_url}"

    try:
        response = urls_table.get_item(Key={"short_url": short_url_in_db})

    except ClientError as err:
        logger.error(
            f"Couldn't get_item from urls table. Here's why: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}"
        )
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, err.response["Error"]["Message"])

    if response.get("Item") is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "short url not found")

    if response.get("Item").get("original_url") is None:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "stored data invalid")

    return RedirectResponse(
        response.get("Item").get("original_url"), HTTPStatus.PERMANENT_REDIRECT
    )
