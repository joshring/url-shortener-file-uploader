import boto3
from botocore.exceptions import ClientError
from http import HTTPStatus
from fastapi import HTTPException

from fastapi import FastAPI, Request
from typing import AsyncGenerator, Any
from contextlib import asynccontextmanager
from environment.env import db_port, db_host, in_lambda_fn, region
import logging

logger = logging.getLogger(__name__)


def create_urls_table(dynamodb):
    """
    Creates an Amazon DynamoDB table storing urls, partitioned on short_url and sorted by user_name
    :return: The newly created table.
    """
    try:
        table = dynamodb.create_table(
            TableName="urls",
            KeySchema=[
                # Partition key
                {
                    "AttributeName": "short_url",
                    "KeyType": "HASH",
                },
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "short_url",
                    "AttributeType": "S",
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()

    except ClientError as err:
        logger.error(
            "Couldn't create table urls. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    else:
        return table


async def dynamodb_conn(request: Request) -> AsyncGenerator[Any, Any]:

    dynamodb = request.state.dynamodb
    yield dynamodb


@asynccontextmanager
async def dynamodb_lifespan(app: FastAPI):

    dynamodb = None

    if in_lambda_fn:
        dynamodb = boto3.resource(
            service_name="dynamodb",
            region_name=region,
        )
        list_tables = [item.name for item in list(dynamodb.tables.all())]

        if "urls" not in list_tables:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="database not available",
            )

        ## Avaiable via: request.state.dynamodb and used in dynamodb_conn()
        yield {"dynamodb": dynamodb}

    else:
        endpoint_url = f"{db_host}:{db_port}"

        dynamodb = boto3.resource(
            service_name="dynamodb",
            endpoint_url=endpoint_url,
            region_name=region,
        )

        list_tables = [item.name for item in list(dynamodb.tables.all())]

        if "urls" not in list_tables:
            create_urls_table(dynamodb)

        ## Avaiable via: request.state.dynamodb and used in dynamodb_conn()
        yield {"dynamodb": dynamodb}
