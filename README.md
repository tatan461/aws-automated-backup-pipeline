# AWS Automated Backup Pipeline

A secure and cost-conscious backup pipeline built with Python, Amazon S3, AWS KMS, IAM, STS, and Terraform.

The project creates compressed backups, uploads them to Amazon S3 with SSE-KMS encryption, verifies integrity with SHA-256, downloads and restores the archive, and enforces least-privilege access through separate IAM roles.

## Architecture

![AWS automated backup pipeline architecture](docs/architecture.png)

The editable Draw.io source is available at:

- [Architecture diagram](docs/architecture.drawio)

## Features

- Compressed backup creation with Python.
- Upload to Amazon S3.
- Server-side encryption with AWS KMS.
- SHA-256 integrity verification.
- Download and restore workflow.
- Separate upload and restore IAM roles.
- Least-privilege S3 and KMS policies.
- Temporary credentials through AWS STS.
- Infrastructure as Code with Terraform.
- Automated tests with Pytest.

## Architecture flow

1. The local backup CLI reads the source directory.
2. Python creates a compressed `tar.gz` archive.
3. The upload role writes the archive to the `backups/` prefix in Amazon S3.
4. Amazon S3 encrypts the object using AWS KMS.
5. The restore role downloads and decrypts the object.
6. The CLI verifies the SHA-256 checksum and restores the archive.

## IAM security model

### Upload role

`automated-backup-upload-role`

Allowed operations:

- `s3:PutObject`
- `s3:AbortMultipartUpload`
- `s3:ListBucket`
- `kms:Encrypt`
- `kms:GenerateDataKey`

The role can write only to:

```text
s3://jhon-aws-backups-2026-portfolio/backups/*
```

### Restore role

`automated-backup-restore-role`

Allowed operations:

- `s3:GetObject`
- `s3:ListBucket`
- `kms:Decrypt`

The restore role cannot upload backup objects.

Both roles are assumed through temporary AWS STS credentials.

## Project structure

```text
.
├── examples/
│   └── sample-data/
├── infra/
│   ├── backup/
│   └── iam/
├── src/
│   └── backup/
├── tests/
├── docs/
│   └── architecture.drawio
├── .gitignore
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.11 or newer.
- AWS CLI configured with an AWS identity allowed to use Terraform.
- Terraform 1.5 or newer.
- An AWS account.
- An S3 bucket.
- An AWS KMS key.

## Installation

Clone the repository:

```bash
git clone [https://github.com/tatan461/aws-automated-backup-pipeline.git](https://github.com/tatan461/aws-automated-backup-pipeline.git)
cd aws-automated-backup-pipeline
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
pip install -e .
```

Install development dependencies:

```bash
pip install pytest
```

## Configure AWS

Set the AWS region:

```bash
export AWS_REGION="us-east-1"
export AWS_DEFAULT_REGION="us-east-1"
```

Verify the active identity:

```bash
aws sts get-caller-identity
```

Do not commit AWS access keys, Terraform state, Terraform plans, or `terraform.tfvars`.

## Deploy the backup infrastructure

Initialize Terraform:

```bash
terraform -chdir=infra/backup init
```

Format and validate:

```bash
terraform -chdir=infra/backup fmt
terraform -chdir=infra/backup validate
```

Review the plan:

```bash
terraform -chdir=infra/backup plan
```

Apply the infrastructure:

```bash
terraform -chdir=infra/backup apply
```

## Deploy IAM roles and policies

Configure the local variables:

```bash
cp infra/iam/terraform.tfvars.example infra/iam/terraform.tfvars
```

Edit `infra/iam/terraform.tfvars` with the real bucket name, KMS key ARN, and trusted user ARN.

Initialize and validate:

```bash
terraform -chdir=infra/iam init
terraform -chdir=infra/iam fmt
terraform -chdir=infra/iam validate
```

Review and apply:

```bash
terraform -chdir=infra/iam plan
terraform -chdir=infra/iam apply
```

## Run the backup workflow

Create a backup:

```bash
python -m backup create examples/sample-data \
  -o backup-output/backup.tar.gz
```

Upload the backup:

```bash
python -m backup upload \
  backup-output/backup.tar.gz \
  --key backups/backup.tar.gz
```

Download the backup:

```bash
python -m backup download \
  backups/backup.tar.gz \
  downloaded.tar.gz
```

Restore the backup:

```bash
python -m backup restore \
  downloaded.tar.gz \
  restore-output
```

Verify the restored content:

```bash
diff -r examples/sample-data \
       restore-output/sample-data
```

No output from `diff` means that the restored files match the originals.

## Tests

Run the test suite:

```bash
pytest
```

## Validation evidence

The complete backup round trip was verified:

- Archive created successfully.
- SHA-256 checksum calculated.
- Backup uploaded to Amazon S3.
- Object encrypted with AWS KMS.
- Backup downloaded and verified.
- Archive restored successfully.
- Upload and restore permissions tested with separate IAM roles.
- Upload role denied read access as expected.

## Cleanup

To remove Terraform-managed IAM and backup infrastructure:

```bash
terraform -chdir=infra/iam destroy
terraform -chdir=infra/backup destroy
```

Review the destroy plan carefully before confirming.

## Security notes

- Never commit AWS credentials.
- Never commit `terraform.tfvars`.
- Never commit Terraform state or plan files.
- Use temporary STS credentials where possible.
- Keep upload and restore permissions separate.
- Restrict access to the required S3 prefix and KMS key.
- Rotate or revoke credentials if they are exposed.

## License

This project is provided for educational and portfolio purposes.