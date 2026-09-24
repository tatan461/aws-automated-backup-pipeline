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

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::${var.bucket_name}/backups/*"
    ]
  }

  statement {
    sid    = "DecryptBackupObjects"
    effect = "Allow"

    actions = [
      "kms:Decrypt"
    ]

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

data "aws_iam_policy_document" "backup_assume_role" {
  statement {
    sid     = "AllowTrustedUserToAssumeBackupRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [var.trusted_user_arn]
    }
  }
}

data "aws_iam_policy_document" "restore_assume_role" {
  statement {
    sid     = "AllowTrustedUserToAssumeRestoreRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [var.trusted_user_arn]
    }
  }
}

resource "aws_iam_role" "backup" {
  name               = "automated-backup-upload-role"
  assume_role_policy = data.aws_iam_policy_document.backup_assume_role.json
}

resource "aws_iam_role" "restore" {
  name               = "automated-backup-restore-role"
  assume_role_policy = data.aws_iam_policy_document.restore_assume_role.json
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = aws_iam_policy.backup.arn
}

resource "aws_iam_role_policy_attachment" "restore" {
  role       = aws_iam_role.restore.name
  policy_arn = aws_iam_policy.restore.arn
}

resource "aws_iam_policy" "assume_backup_role" {
  name        = "assume-automated-backup-upload-role"
  description = "Allow the trusted user to assume the backup upload role"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = aws_iam_role.backup.arn
      }
    ]
  })
}

resource "aws_iam_policy" "assume_restore_role" {
  name        = "assume-automated-backup-restore-role"
  description = "Allow the trusted user to assume the backup restore role"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = aws_iam_role.restore.arn
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "assume_backup_role" {
  user       = "cloud-resume-deploy"
  policy_arn = aws_iam_policy.assume_backup_role.arn
}

resource "aws_iam_user_policy_attachment" "assume_restore_role" {
  user       = "cloud-resume-deploy"
  policy_arn = aws_iam_policy.assume_restore_role.arn
}