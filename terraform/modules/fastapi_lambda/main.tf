locals {
    common_tags = {
        Terraform   = "true"
        Environment = var.environment_name
        module_name = var.module_name
    }
    
    lambda_fn_name = "fastapi-lambda-fn-${var.environment_name}"
}

data "aws_iam_policy_document" "fastapi_assume_role" {
    
    # Assume lambda service role
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

resource "aws_iam_role" "fastapi_role" {
    name               = "fastapi_role"
    assume_role_policy = data.aws_iam_policy_document.fastapi_assume_role.json
}

#========================================
# Add policies

data "aws_iam_policy_document" "fastapi_iam_policy_doc" {

    # Allow logging from lambda
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
        ]
        resources = ["arn:aws:logs:*:*:*"]
    }
    
    # Allow ListAndDescribe on dynamodb
    statement {
        effect = "Allow"
        actions = [
            "dynamodb:List*",
            "dynamodb:DescribeReservedCapacity*",
            "dynamodb:DescribeLimits",
            "dynamodb:DescribeTimeToLive"
        ]
        resources = ["*"]
    }
    
    # Allow actions on urls dynamodb table
    statement {
        effect = "Allow"
        actions = [
            "dynamodb:DescribeTable",
            "dynamodb:CreateTable",
            "dynamodb:Get*",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:Update*",
            "dynamodb:PutItem"
        ]
        resources = [var.dynamodb_urls_table_arn]
    }
	
	# Allow writing file to S3
    statement {
        effect = "Allow"
        actions = [
            "s3:PutObject",
        ]
        resources = ["arn:aws:s3:::${var.s3_bucket_name}/*"]
    }   
	
	
	# Allow access to lambda metadata
    statement {
        effect = "Allow"
        actions = [
            "lambda:GetFunctionUrlConfig",
			"lambda:GetFunction",
			"lambda:GetFunctionConfiguration",
        ]
		resources = ["*"]
    }   										   
	
	
}


resource "aws_iam_policy" "fastapi_iam_policy" {
    name        = "fastapi_iam_policy"
    policy      = data.aws_iam_policy_document.fastapi_iam_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "fastapi_iam_policy_attach" {
    role       = aws_iam_role.fastapi_role.name
    policy_arn = aws_iam_policy.fastapi_iam_policy.arn
}


# =================================
# Lambda's FastAPI code
data "archive_file" "fastapi_code" {
    type        = "zip"
    source_dir  = "${path.module}/../../../api"
    output_path = "lambda_function_payload.zip"
    excludes    = [
        "packages/*",
        "__pycache__/*",
        ".venv/*",
        "*/__pycache__/*",
    ]
}

# =================================
# Manage the dependencies as a layer
# dependencies are packaged via the following command in the python api directory:
# pip install --target ./packages/ -r requirements.txt
data "archive_file" "lambda_layer" {
    type        = "zip"
    source_dir  = "${path.module}/../../../api/packages"
    output_path = "lambda_layer.zip"
}
resource "aws_lambda_layer_version" "fastapi_lambda_layer" {
    filename   = "lambda_layer.zip"
    layer_name = "fastapi_layer"

    compatible_runtimes = ["python3.13"]
}
# =================================

resource "aws_lambda_function" "fastapi_lambda" {
    filename      	= "lambda_function_payload.zip"
    function_name 	= local.lambda_fn_name
    role          	= aws_iam_role.fastapi_role.arn
    handler       	= "main.lambda_handler"
	memory_size 	= 512
	timeout 		= 10

    source_code_hash = data.archive_file.fastapi_code.output_base64sha256
    layers = [aws_lambda_layer_version.fastapi_lambda_layer.arn]

    runtime = "python3.13"

    environment {
        variables = {
            REGION          	= var.aws_region
            S3_BUCKET_NAME  	= var.s3_bucket_name
			S3_BUCKET_HTTPS_URL = var.s3_files_https_url
			FRONTEND_URL 		= "https://${var.frontend_url}"
			LAMBDA_FN_NAME 		= local.lambda_fn_name
        }
    }
}

resource "aws_lambda_permission" "fastapi_lambda_permissions" {
    statement_id  = "AllowAPIGatewayInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.fastapi_lambda.function_name
    principal     = "apigateway.amazonaws.com"
}


resource "aws_cloudwatch_log_group" "fastapi_log_group" {
    name              = "/aws/lambda/${local.lambda_fn_name}"
    retention_in_days = 3
}


resource "aws_lambda_function_url" "fastapi_lambda" {
	function_name      = aws_lambda_function.fastapi_lambda.function_name
	authorization_type = "NONE"
}

