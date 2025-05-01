# from fastapi import APIRouter, Body, Depends, Request, status, Query, Path
from fastapi.exceptions import HTTPException
from http import HTTPStatus
from pydantic import (
    ValidationError,
    HttpUrl,
    BaseModel,
    Field,
    model_validator,
)

from enum import Enum


class UrlType(str, Enum):
    site_url = "site_url"
    file_url = "file_url"


def validate_http_url(url_str: str, url_name: str):
    """
    HttpUrl does not serialise correctly so we use str and validate here instead
    See: https://github.com/pydantic/pydantic/discussions/6395
    """
    try:
        HttpUrl(url_str)
    except ValidationError as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, f"invalid {url_name}")


class UrlInDB(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # enum string values
    }

    short_url: str
    original_url: str
    url_type: UrlType
    user_name: str = Field(min_length=1)

    @model_validator(mode="after")
    def url_validator(self) -> "Url":
        validate_http_url(self.original_url, "original_url")
        return self


class UrlRequest(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # enum string values
    }

    original_url: str

    @model_validator(mode="after")
    def url_validator(self) -> "Url":
        validate_http_url(self.original_url, "original_url")
        return self


class Url(BaseModel):
    model_config = {
        "use_enum_values": True,  # enum string values
    }

    short_url: str
    original_url: str
    url_type: UrlType

    @model_validator(mode="after")
    def url_validator(self) -> "Url":
        validate_http_url(self.original_url, "original_url")
        return self


class UserUrls(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # enum string values
    }
    user_name: str
    urls: list[Url]


class UrlRedirect(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # enum string values
    }

    short_url: str
    original_url: str
    url_type: UrlType

    @model_validator(mode="after")
    def url_validator(self) -> "UrlRedirect":
        validate_http_url(self.original_url, "original_url")
        return self
