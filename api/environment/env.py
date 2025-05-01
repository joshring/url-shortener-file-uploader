from os import environ
from pydantic import HttpUrl, ValidationError
from urllib.request import Request, urlopen
import logging
import boto3

logger = logging.getLogger("__name__")

frontend_url = environ.get("FRONTEND_URL")
if frontend_url is None:
    raise ValueError("missing env var: FRONTEND_URL")

region = environ.get("REGION")
if region is None:
    raise ValueError("missing env var: REGION")

in_lambda_fn = False
aws_execution_env = environ.get("AWS_EXECUTION_ENV")
if aws_execution_env is not None:
    in_lambda_fn = True


db_host = environ.get("DB_HOST")
if db_host is None and not in_lambda_fn:
    raise ValueError("missing env var: DB_HOST")

db_port = environ.get("DB_PORT")
if db_port is None and not in_lambda_fn:
    raise ValueError("missing env var: DB_PORT")
if db_port is not None:
    db_port = int(db_port)


# ====================================
# The webserver host address
server_host = None

if in_lambda_fn:

    lambda_fn_name = environ.get("LAMBDA_FN_NAME")
    if lambda_fn_name is None:
        raise ValueError("missing env var: LAMBDA_FN_NAME")

    lambda_client = boto3.client("lambda")
    try:
        response = lambda_client.get_function_url_config(FunctionName=lambda_fn_name)
        server_host = response.get("FunctionUrl")
        if server_host is None:
            raise ValueError("'FunctionUrl' not found in the response")

    except Exception as err:
        raise ValueError(f"Error retrieving function URL config: {err}")

else:
    server_host = environ.get("SERVER_HOST")
    if server_host is None:
        raise ValueError("missing env var: SERVER_HOST")

# remove any newlines etc
server_host = server_host.replace("\n", "")

## remove any accidental trailing slash
if server_host.endswith("/"):
    server_host = server_host[:-1]


s3_bucket_name = environ.get("S3_BUCKET_NAME")
if s3_bucket_name is None:
    raise ValueError("missing env var: S3_BUCKET_NAME")


s3_bucket_https_url = environ.get("S3_BUCKET_HTTPS_URL")
if s3_bucket_https_url is None:
    raise ValueError("missing env var: S3_BUCKET_HTTPS_URL")
