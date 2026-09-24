terraform {
  required_version = ">= 1.9.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for the backup resources."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name for backup archives."
  type        = string
}

variable "project_name" {
  description = "Project identifier used for resource naming."
  type        = string
  default     = "aws-automated-backup-pipeline"
}

variable "archive_after_days" {
  description = "Days before transitioning current objects to Glacier Deep Archive."
  type        = number
  default     = 180
}

variable "expire_after_days" {
  description = "Days before expiring current backup objects."
  type        = number
  default     = 730
}

resource "aws_kms_key" "backup" {
  description             = "KMS key for ${var.project_name} backup archives"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
    Purpose   = "Backup encryption"
  }
}

resource "aws_kms_alias" "backup" {
  name          = "alias/${var.project_name}"
  target_key_id = aws_kms_key.backup.key_id
}

resource "aws_s3_bucket" "backups" {
  bucket = var.bucket_name

  tags = {
    Project   = var.project_name
    ManagedBy = "Terraform"
    Purpose   = "Encrypted backup storage"
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.backup.arn
      sse_algorithm     = "aws:kms"
    }

    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "archive-and-expire-backups"
    status = "Enabled"

    filter {
      prefix = "backups/"
    }

    transition {
      days          = var.archive_after_days
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = var.expire_after_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.expire_after_days
    }
  }

  depends_on = [aws_s3_bucket_versioning.backups]
}

output "bucket_name" {
  description = "Backup bucket name."
  value       = aws_s3_bucket.backups.bucket
}

output "bucket_arn" {
  description = "Backup bucket ARN."
  value       = aws_s3_bucket.backups.arn
}

output "kms_key_arn" {
  description = "Backup KMS key ARN."
  value       = aws_kms_key.backup.arn
}

output "kms_alias" {
  description = "Backup KMS alias."
  value       = aws_kms_alias.backup.name
}