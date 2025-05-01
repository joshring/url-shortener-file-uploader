resource "aws_dynamodb_table" "dynamodb_urls_table" {
    name           	= "urls"
    read_capacity  	= 1
    write_capacity	= 1
    hash_key       	= "short_url"

	attribute {
        name = "short_url"
        type = "S"
    }
}
