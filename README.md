# Run locally


## Start Local DynamoDB
```bash
cd api
docker compose up
```

## Start API
```bash
cd api
```
Create your virtual env
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API
```bash
FRONTEND_URL=http://localhost:3000 REGION=eu-west-1 S3_BUCKET_NAME=file-upload-store--dev S3_BUCKET_HTTPS_URL=d2vym4pzdzqjx3.cloudfront.net DB_PORT=8888 DB_HOST=http://localhost SERVER_HOST=http://localhost:8080 fastapi dev main.py --port 8080
```

Run the integration tests
```bash
cd api/tests

FRONTEND_URL=http://localhost:3000 REGION=eu-west-1 S3_BUCKET_NAME=file-upload-store--dev S3_BUCKET_HTTPS_URL=d2vym4pzdzqjx3.cloudfront.net DB_PORT=8888 DB_HOST=http://localhost SERVER_HOST=http://localhost:8080 pytest -vv -s -W ignore::DeprecationWarning
```


## Start NextJS
```bash
cd nextjs 
npm run dev 
```



# Build and Run Deployment

## Build Static NextJS App 
> **Note:**
> We will need to rebuild nextjs once we have infra to set up
> we need the `NEXT_PUBLIC_SERVER_HOST` for the lambda function URL inside `.env.production`

```bash
cd nextjs 
npm run build 
```

## Build Python's lambda layer packages

```bash
cd api 
pip install -r requirements.txt -t packages/python/
```

## Deploy infrastructure inside terraform/dev
> **Note:**
> This updates nextjs/.env.production with the lambda's URL

```bash
cd terraform/dev
terraform init
terraform apply
```

## Rebuild NextJS as now nextjs/.env.production is now populated with the lambda's URL
```bash
cd nextjs 
npm run build 
```

## Repeat and redeploy NextJS with the lambda API's URL
```bash
cd terraform/dev
terraform apply
```