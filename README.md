<div align="center">

# AWS Automated Backup Pipeline

**A secure, encrypted, and integrity-verified backup and restore workflow built with AWS, Python, and Terraform.**

[Architecture](#architecture) · [Features](#features) · [Deployment](#deployment) · [Testing](#testing)

![AWS](https://img.shields.io/badge/Cloud-AWS-232F3E?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Runtime-Python-3776AB?logo=python&logoColor=white)
![Boto3](https://img.shields.io/badge/AWS%20SDK-Boto3-FF9900?logo=amazonaws&logoColor=white)
![Security](https://img.shields.io/badge/Encryption-SSE--KMS-DC3545)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

> A Terraform-managed AWS backup workflow that packages local data, stores it in encrypted Amazon S3, and verifies integrity after restoration.

---

## Overview

This project implements a practical backup and disaster-recovery workflow using Amazon S3, AWS KMS, IAM, STS temporary credentials, Python, and Terraform.

The pipeline creates a compressed archive from a local directory, uploads it to a private S3 bucket with SSE-KMS encryption, and restores it through a separate read and decrypt workflow. SHA-256 verification confirms that the restored data matches the original backup.

The architecture is designed around least privilege and separation of duties:

- The upload role can write backup objects.
- The restore role can read and decrypt backup objects.
- AWS STS provides temporary credentials.
- S3 stores encrypted and versioned backup objects.
- SHA-256 detects corrupted or incomplete restores.

## Why this project

Reliable backups are only useful when they are protected, recoverable, and verifiable.

This project explores the engineering decisions required to build a small but secure AWS backup workflow:

- Protect data at rest with AWS KMS.
- Separate upload and restore responsibilities.
- Avoid long-lived operational credentials.
- Provision infrastructure repeatably with Terraform.
- Detect data corruption during restore.
- Keep operational cost low by using managed AWS services.

## Architecture

![AWS Automated Backup Pipeline architecture](docs/architecture.png)

### Flow summary

```text
Local source directory
        |
        v
Python CLI creates tar.gz archive
        |
        v
Upload role obtains temporary STS credentials
        |
        v
Amazon S3 stores the object with SSE-KMS
        |
        v
Restore role reads and decrypts the object
        |
        v
Python CLI extracts and verifies SHA-256
        |
        v
Restored files
```

## Features

- Compressed `tar.gz` backup archives.
- Private Amazon S3 backup storage.
- Server-side encryption with AWS KMS.
- Separate upload and restore IAM roles.
- Temporary AWS credentials through STS.
- S3 versioning for backup object protection.
- Lifecycle configuration for storage management.
- Public-access blocking.
- SHA-256 integrity verification after restore.
- Terraform-managed infrastructure.
- Unit tests for backup and storage operations.

## Main components

| Component | Purpose |
|---|---|
| Python CLI | Creates archives and verifies restored data |
| Amazon S3 | Stores encrypted backup objects |
| AWS KMS | Provides encryption at rest |
| AWS IAM | Separates upload and restore permissions |
| AWS STS | Provides temporary credentials |
| Terraform | Provisions the AWS infrastructure |
| SHA-256 | Verifies backup integrity after restore |

## Security and operational notes

- S3 public access is blocked.
- Backup objects are encrypted with SSE-KMS.
- Upload and restore permissions are isolated through separate IAM roles.
- Temporary STS credentials are preferred over long-lived access keys.
- AWS credentials must never be stored in source files.
- `terraform.tfvars` must remain local and must not be committed.
- Terraform state files must be protected and excluded from version control.
- Restore operations should be considered successful only after SHA-256 verification passes.
- Integration testing should use a dedicated AWS environment to avoid unexpected charges.

## Requirements

- Python 3.11+
- Terraform 1.5+
- AWS CLI
- An AWS account for deployment or integration testing
- An AWS identity with permission to provision the required resources

## Installation

```bash
git clone [https://github.com/tatan461/aws-automated-backup-pipeline.git](https://github.com/tatan461/aws-automated-backup-pipeline.git)
cd aws-automated-backup-pipeline

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Deployment

Terraform configuration is located in:

```text
infra/backup/
```

The configuration includes:

- S3 backup bucket.
- SSE-KMS encryption.
- S3 versioning.
- Public-access blocking.
- Lifecycle configuration.
- Example deployment variables.

Create a local variables file:

```bash
cd infra/backup
cp terraform.tfvars.example terraform.tfvars
```

Review the values before running Terraform:

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

Never commit:

```text
terraform.tfvars
*.tfstate
*.tfstate.*
.env
AWS credentials
```

## Usage

Inspect the available command options:

```bash
python -m src.backup --help
python -m src.s3_storage --help
```

The intended operational sequence is:

1. Select the source directory.
2. Create the compressed backup archive.
3. Upload the archive using the upload role.
4. Store the object key and expected SHA-256 digest.
5. Restore the backup using the restore role.
6. Extract the archive.
7. Verify the SHA-256 digest.
8. Treat the restore as successful only if verification passes.

See the [restore runbook](docs/restore-runbook.md) for the recovery procedure.

## Testing

Run the unit tests:

```bash
python -m pytest -q
```

Optional quality checks:

```bash
ruff check .
bandit -r src
```

Validate the Terraform configuration:

```bash
cd infra/backup
terraform fmt -check
terraform validate
```

The test suite covers backup creation and S3 storage operations. Recommended additional test cases include:

- Missing input files.
- S3 permission errors.
- Empty or corrupted objects.
- SHA-256 mismatches.
- Invalid configuration.
- Failed download or restore operations.

## Project structure

```text
.
├── docs/
│   ├── architecture.md
│   ├── architecture.png
│   ├── cost-model.md
│   └── restore-runbook.md
├── examples/
├── infra/
│   └── backup/
│       ├── main.tf
│       ├── terraform.tfvars.example
│       └── .terraform.lock.hcl
├── src/
│   ├── backup.py
│   └── s3_storage.py
├── tests/
│   ├── test_backup.py
│   └── test_s3_storage.py
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Documentation

- [Architecture notes](docs/architecture.md)
- [Restore runbook](docs/restore-runbook.md)
- [Cost model](docs/cost-model.md)

## Related project

This project complements my [Cloud Resume Challenge + AI (Bedrock)](https://github.com/tatan461/cloud-resume-ai).

Together, these projects demonstrate:

- Serverless AWS architecture.
- Infrastructure as Code with Terraform.
- Secure IAM design.
- Temporary cloud credentials.
- Practical cloud operations across application and infrastructure workloads.

## Author

**Jonathan Angel Gonzalez**

Junior Cloud Engineer · AWS Certified Specialist

[![GitHub](https://img.shields.io/badge/GitHub-tatan461-181717?logo=github&logoColor=white)](https://github.com/tatan461)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Jonathan%20Angel%20Gonzalez-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jonathan-angel-gonzalez-0543b441a/)

## License

This project is licensed under the [MIT License](LICENSE).