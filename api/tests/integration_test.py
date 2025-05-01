import requests
import time
from http import HTTPStatus
import boto3
from botocore.exceptions import ClientError
import logging
import io
from os import environ

logger = logging.getLogger("__name__")


def db_cleanup():
    """
    Give a clean urls table for each test run
    """
    dynamodb = boto3.resource(
        service_name="dynamodb",
        endpoint_url="http://localhost:8888",
        region_name="eu-west-1",
    )

    urls_table = dynamodb.Table("urls")

    resp = urls_table.scan()
    if len(resp["Items"]) == 0:
        return

    primary_keys = [item["short_url"] for item in resp["Items"]]

    for primary_key in primary_keys:
        urls_table.delete_item(Key={"short_url": primary_key})

    resp = urls_table.scan()
    assert len(resp["Items"]) == 0


def test_post_url():

    db_cleanup()

    resp = requests.post(
        url="http://localhost:8080/urls",
        data=f"""
        {{
            "original_url": "https://www.gentoo.org"
        }}
        """,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == HTTPStatus.OK

    resp_json = resp.json()

    expected_response = {
        "short_url": resp_json["short_url"],
        "original_url": "https://www.gentoo.org",
        "url_type": "site_url",
    }

    assert resp_json == expected_response


def test_redirect_to_short_url():

    db_cleanup()

    # Add data
    resp1 = requests.post(
        url="http://localhost:8080/urls",
        data=f"""
        {{
            "original_url": "https://www.gentoo.org"
        }}
        """,
        headers={"Content-Type": "application/json"},
    )

    assert resp1.status_code == HTTPStatus.OK

    # Test redirect
    resp2 = requests.get(
        url=resp1.json()["short_url"],
    )
    # Check for redirects
    assert len(resp2.history) == 1

    assert resp2.history[0].status_code == HTTPStatus.PERMANENT_REDIRECT
    assert resp2.history[0].url == resp1.json()["short_url"]


def test_post_invalid_url():

    db_cleanup()

    resp = requests.post(
        url="http://localhost:8080/urls",
        data=f"""
        {{
            "original_url": "invalid url here"
        }}
        """,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {"detail": "invalid original_url"}


def test_get_urls_empty():

    db_cleanup()

    resp = requests.get(
        url="http://localhost:8080/urls",
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"urls": [], "user_name": "hard_coded_user"}


def test_get_urls_populated():

    db_cleanup()

    ## Populate with data
    resp1 = requests.post(
        url="http://localhost:8080/urls",
        data=f"""
        {{
            "original_url": "https://www.gentoo.org"
        }}
        """,
        headers={"Content-Type": "application/json"},
    )
    assert resp1.status_code == HTTPStatus.OK

    ## Test we can retrieve it
    resp2 = requests.get(
        url="http://localhost:8080/urls",
    )
    assert resp2.status_code == HTTPStatus.OK
    expected_json = {
        "user_name": "hard_coded_user",
        "urls": [
            {
                "original_url": "https://www.gentoo.org",
                "short_url": resp1.json()["short_url"],
                "url_type": "site_url",
            },
        ],
    }

    assert resp2.json() == expected_json


# def test_post_files():
#     """
#     Note this integration test requires valid AWS creds in your env,
#       and a valid S3 bucket & cloud formation for https, to run correctly
#     """

#     db_cleanup()

#     s3_bucket_https_url = environ.get("S3_BUCKET_HTTPS_URL")
#     if s3_bucket_https_url is None:
#         raise ValueError("S3_BUCKET_HTTPS_URL env var was not set")

#     ## Populate with data
#     resp1 = requests.post(
#         url="http://localhost:8080/files/testing_example_file",
#         files={"file": io.BytesIO(b"example file content")},
#     )

#     assert resp1.status_code == HTTPStatus.OK

#     original_file_url = f"https://{s3_bucket_https_url}/testing_example_file"

#     expected_json = {
#         "original_url": original_file_url,
#         "short_url": resp1.json()["short_url"],
#         "url_type": "file_url",
#     }

#     assert resp1.json() == expected_json

#     ## Test we can retrieve it
#     resp2 = requests.get(
#         url="http://localhost:8080/urls",
#     )
#     assert resp2.status_code == HTTPStatus.OK

#     expected_json = {
#         "user_name": "hard_coded_user",
#         "urls": [
#             {
#                 "original_url": original_file_url,
#                 "short_url": resp1.json()["short_url"],
#                 "url_type": "file_url",
#             },
#         ],
#     }

#     assert resp2.json() == expected_json
