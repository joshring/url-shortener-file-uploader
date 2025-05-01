locals {
	s3_origin_id = "${var.s3_bucket_name}-origin"
}

resource "aws_s3_bucket" "bucket" {
    bucket = var.s3_bucket_name
    force_destroy = true
    
    lifecycle {
        prevent_destroy = false
    }
}


resource "aws_s3_bucket_public_access_block" "bucket" {
    bucket = aws_s3_bucket.bucket.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "bucket" {
    bucket = aws_s3_bucket.bucket.id
    rule {
        object_ownership = "BucketOwnerPreferred"
    }
}

resource "aws_s3_bucket_acl" "bucket" {
    depends_on = [
        aws_s3_bucket_ownership_controls.bucket,
        aws_s3_bucket_public_access_block.bucket,
    ]

    bucket = aws_s3_bucket.bucket.id
    acl    = "public-read"
}

# Docs https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document
data "aws_iam_policy_document" "public_access" {
    statement {
        principals {
            type  = "*"
            identifiers = ["*"]
        }

        actions = [
            "s3:GetObject",
        ]

        effect = "Allow"

        resources = [
            aws_s3_bucket.bucket.arn,
            "${aws_s3_bucket.bucket.arn}/*",
        ]
    }
}


resource "aws_s3_bucket_policy" "public_access" {
    bucket = aws_s3_bucket.bucket.id
    policy = data.aws_iam_policy_document.public_access.json
	
	depends_on = [aws_s3_bucket_acl.bucket]
}


resource "aws_s3_bucket_cors_configuration" "cors_config" {
    bucket = aws_s3_bucket.bucket.id

    cors_rule {
        allowed_headers = ["*"]
        allowed_methods = ["PUT", "POST"]
        allowed_origins = ["*"]
        expose_headers  = ["ETag"]
        max_age_seconds = 3000
    }

    cors_rule {
        allowed_methods = ["GET"]
        allowed_origins = ["*"]
    }
}

resource "aws_cloudfront_origin_access_control" "bucket_distribution_oac" {
	name                              = "bucket_oac"
	origin_access_control_origin_type = "s3"
	signing_behavior                  = "always"
	signing_protocol                  = "sigv4"
}

# cloudfront for HTTPS support
resource "aws_cloudfront_distribution" "s3_distribution" {
	origin {
		domain_name              = aws_s3_bucket.bucket.bucket_regional_domain_name
		origin_access_control_id = aws_cloudfront_origin_access_control.bucket_distribution_oac.id
		origin_id                = local.s3_origin_id
	}

	enabled             = true
	is_ipv6_enabled     = true

  	# aliases = ["url-shortener-files.co.uk"]

	default_cache_behavior {
		allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
		cached_methods   = ["GET", "HEAD"]
		target_origin_id = local.s3_origin_id

		forwarded_values {
			query_string = true
			headers      = [
				"date", 
				"keep-alive",
				"origin",
				"content-type",
			]

			cookies {
				forward = "all"
			}
		}

		viewer_protocol_policy = "redirect-to-https"
		min_ttl                = 0
		default_ttl            = 3600
		max_ttl                = 86400
	}

  	price_class = "PriceClass_100"

	restrictions {
		geo_restriction {
			restriction_type = "none"
		}
	}

	viewer_certificate {
		cloudfront_default_certificate = true
	}
}

