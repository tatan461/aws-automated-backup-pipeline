terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_iam_policy_document" "backup" {
  statement {
    sid    = "ListBackupPrefix"
    effect = "Allow"

    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.bucket_name}"]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["backups/*"]
    }
  }

  statement {
    sid    = "UploadBackupObjects"
    effect = "Allow"

    actions = [
      "s3:AbortMultipartUpload",
      "s3:PutObject"
    ]

    resources = [
      "arn:aws:s3:::${var.bucket_name}/backups/*"
    ]
  }

  statement {
    sid    = "EncryptBackupObjects"
    effect = "Allow"

    actions = [
      "kms:Encrypt",
      "kms:GenerateDataKey"
    ]

    resources = [var.kms_key_arn]
  }
}

data "aws_iam_policy_document" "restore" {
  statement {
    sid    = "ListBackupPrefix"
    effect = "Allow"

    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.bucket_name}"]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["backups/*"]
    }
  }

  statement {
    sid    = "DownloadBackupObjects"
    effect = "Allow"

    actions = ["s3:GetObject"]
    resources = [
      "arn:aws:s3:::${var.bucket_name}/backups/*"
    ]
  }

  statement {
    sid    = "DecryptBackupObjects"
    effect = "Allow"

    actions   = ["kms:Decrypt"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_policy" "backup" {
  name        = "automated-backup-upload"
  description = "Upload encrypted backup objects to the backup bucket"
  policy      = data.aws_iam_policy_document.backup.json
}

resource "aws_iam_policy" "restore" {
  name        = "automated-backup-restore"
  description = "Download and decrypt backup objects from the backup bucket"
  policy      = data.aws_iam_policy_document.restore.json
}