# URL shortener and file uploader to S3
 

## Starting DynamoDB Using Docker Compose
```bash
docker compose up --build
```

## Create Virtual Environment
```bash
python3 -m venv .venv
```

## Activate Virtual Environment
```bash
source .venv/bin/activate
```

## Install Dependencies into the virtual environment
```bash
pip install -r requirements.txt
```

## Create lambda layer packages
```bash
pip install -r requirements.txt -t packages/python/
```

#### Running The API
```bash
FRONTEND_URL=http://localhost:3000 REGION=eu-west-1 S3_BUCKET_NAME=file-upload-store--dev S3_BUCKET_HTTPS_URL=d2vym4pzdzqjx3.cloudfront.net DB_PORT=8888 DB_HOST=http://localhost SERVER_HOST=http://localhost:8080 fastapi dev main.py --port 8080
```

#### Running The Integration Tests
Note: AWS' boto3 library has some deprecation warnings that I have silenced so they don't pollute the tests

```bash
FRONTEND_URL=http://localhost:3000 REGION=eu-west-1 S3_BUCKET_NAME=file-upload-store--dev S3_BUCKET_HTTPS_URL=d2vym4pzdzqjx3.cloudfront.net DB_PORT=8888 DB_HOST=http://localhost SERVER_HOST=http://localhost:8080 pytest -vv -s -W ignore::DeprecationWarning
```

