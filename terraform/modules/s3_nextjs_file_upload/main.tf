locals {
	nextjs_filepath = "${path.module}/../../../nextjs/out"

	content_type_map = {
		"js" 	= "text/javascript"
		"html" 	= "text/html"
		"css"  	= "text/css"
		"json" 	= "application/json"
		"svg"	= "image/svg+xml" 
		"jpeg" 	= "image/jpeg"
		"png"	= "image/png"
		"ico" 	= "image/x-icon"
		"otf"	= "application/x-font-opentype"
		"ttf"	= "application/x-font-ttf"
		"woff" 	= "application/font-woff"
		"woff2" = "application/font-woff2"
	}
}

# Write to the nextjs/.env.production the URL of the API lambda function
resource "local_file" "write_nextjs_env_production" {
	
	content  = "NEXT_PUBLIC_SERVER_HOST=${trimsuffix(var.fastapi_lambda_function_url, "/")}"
	filename = "${path.module}/../../../nextjs/.env.production"
}


# Upload the NextJS static build
resource "aws_s3_object" "nextjs_file_upload" {
	for_each 		= fileset(local.nextjs_filepath, "**")
	bucket 			= var.s3_bucket_id
	key    			= each.key
	source 			= "${local.nextjs_filepath}/${each.value}"
	etag   			= filemd5("${local.nextjs_filepath}/${each.value}")
	
	# Lookup the Content-Type for each filetype
	content_type 	= lookup(
		local.content_type_map, 
		reverse(split(".", "${local.nextjs_filepath}/${each.value}"))[0],
		"binary/octet-stream" # default
	)
}