output "frontend_url" {
    value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "s3_bucket_id" {
    value = aws_s3_bucket.nextjs_bucket.id
}

