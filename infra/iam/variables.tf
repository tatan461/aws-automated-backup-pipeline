variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  type = string
}

variable "kms_key_arn" {
  type = string
}