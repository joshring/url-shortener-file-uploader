
locals {
    environment_name    	= "dev"
    aws_region          	= "eu-west-1"
    aws_account_id      	= "428409803521"
    s3_files_bucket_name    = "file-upload-store--${local.environment_name}"
	s3_nextjs_bucket_name 	= "nextjs-files-store--${local.environment_name}"
}

module "s3_nextjs" {
    source                  = "../modules/s3_nextjs"
    environment_name        = local.environment_name
    s3_bucket_name          = local.s3_nextjs_bucket_name
}

module "s3_files" {
    source              	= "../modules/s3_files"
    environment_name    	= local.environment_name
    s3_bucket_name         	= local.s3_files_bucket_name
}

module "dynamodb" {
    source = "../modules/dynamodb"
}

module "fastapi_lambda" {
    source                  = "../modules/fastapi_lambda"
    dynamodb_urls_table_arn = module.dynamodb.dynamodb_urls_table_arn
    environment_name        = local.environment_name
    s3_bucket_name          = local.s3_files_bucket_name
	s3_files_https_url 		= module.s3_files.s3_files_https_url
    aws_region              = local.aws_region
	frontend_url 			= module.s3_nextjs.frontend_url
	aws_account_num 		= local.aws_account_id
	
}

module "s3_nextjs_file_upload" {
	source                  	= "../modules/s3_nextjs_file_upload"
	s3_bucket_id 				= module.s3_nextjs.s3_bucket_id
	fastapi_lambda_function_url = module.fastapi_lambda.fastapi_lambda_function_url
}

