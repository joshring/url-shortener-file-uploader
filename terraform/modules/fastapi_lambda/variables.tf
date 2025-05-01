variable "environment_name" {
    type = string
}

variable "module_name" {
    type    = string
    default = "fastapi_lambda"
}

variable "aws_region" {
    type    = string
}

variable "dynamodb_urls_table_arn" {
    type = string
}

variable "s3_bucket_name" {
    type = string
}

variable "frontend_url" {
    type = string
}

variable "aws_account_num" {
    type = string
}

variable "s3_files_https_url" {
    type = string
}

