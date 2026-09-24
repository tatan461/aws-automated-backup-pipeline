# AWS Automated Backup Pipeline

A cost-conscious backup and disaster-recovery pipeline built with Python, Boto3, Amazon S3, AWS KMS, Terraform, and a restore workflow that verifies file integrity with SHA-256.

> Portfolio project focused on secure object storage, isolated access roles, encrypted backups, infrastructure as code, and repeatable restore operations.

## Overview

This project packages a local source directory into a compressed archive, uploads it to Amazon S3 with server-side KMS encryption, and restores it through a separate read/decrypt workflow.

The infrastructure is defined with Terraform under `infra/backup/`.

The design intentionally separates upload and restore permissions:

- The upload role can write backup objects.
- The restore role can read backup objects and use the required decryption permission.
- AWS STS is used as the intended source of temporary credentials.
- SHA-256 verification detects corruption or an incomplete restore.

## Architecture

![AWS Automated Backup Pipeline architecture](docs/architecture.png)

The main flow is:

```text
Source directory
    -> Python CLI creates tar.gz archive
    -> Upload role obtains temporary credentials
    -> Amazon S3 stores the object with SSE-KMS
    -> Restore role reads and decrypts the object
    -> Python CLI extracts and verifies SHA-256
    -> Restored output
```

See the supporting documentation:

- [Architecture notes](docs/architecture.md)
- [Restore runbook](docs/restore-runbook.md)
- [Cost model](docs/cost-model.md)

## Security model

The project is designed around least privilege and separation of duties.

- S3 public access is blocked.
- Backup objects are encrypted at rest with SSE-KMS.
- Upload and restore permissions are granted to separate IAM roles.
- Long-lived AWS access keys must not be committed to the repository.
- STS temporary credentials are preferred for operational access.
- Restore verification fails when the calculated SHA-256 does not match the expected digest.
- Terraform state and local variable files must remain outside version control.

This repository contains no production credentials. Configure AWS access through an approved local profile, environment variables, or an external identity provider.

## Repository structure

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
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

## Requirements

- Python 3.11+
- Terraform 1.5+
- AWS CLI
- An AWS account for integration testing
- An AWS identity with permissions to provision the required resources
- `pytest` for tests

Use a non-root AWS identity for normal development and testing.

## Installation

```bash
git clone [https://github.com/tatan461/aws-automated-backup-pipeline.git](https://github.com/tatan461/aws-automated-backup-pipeline.git)
cd aws-automated-backup-pipeline

python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## AWS configuration

Do not hard-code credentials in source files. Use an AWS profile or environment variables:

```bash
aws configure --profile backup-lab

export AWS_PROFILE=backup-lab
export AWS_REGION=eu-west-1
```

Verify the active identity:

```bash
aws sts get-caller-identity
```

Never commit:

- Access keys.
- Secret keys.
- `.env` files.
- `terraform.tfvars`.
- Terraform state files.
- Temporary credentials.

## Terraform deployment

Terraform configuration is located under:

```text
infra/backup/
```

The current configuration includes:

- Amazon S3 backup bucket.
- Server-side encryption with AWS KMS.
- S3 versioning.
- Public-access blocking.
- Lifecycle configuration.
- Terraform variables documented in `terraform.tfvars.example`.
- Provider lock file committed for reproducible initialization.

Create a local variables file:

```bash
cd infra/backup
cp terraform.tfvars.example terraform.tfvars
```

Review and edit the values before continuing.

Initialize Terraform:

```bash
terraform init
```

Format and validate the configuration:

```bash
terraform fmt -check
terraform validate
```

Review the execution plan:

```bash
terraform plan -var-file="terraform.tfvars"
```

Apply the infrastructure only after reviewing the plan:

```bash
terraform apply -var-file="terraform.tfvars"
```

When the environment is no longer required, remove the resources carefully:

```bash
terraform destroy -var-file="terraform.tfvars"
```

Do not commit `terraform.tfvars`, Terraform state files, or `.terraform/` contents, except for the provider lock file.

## Usage

The exact CLI surface is kept in the Python modules and may evolve while the project is being developed. Inspect the available options with:

```bash
python -m src.backup --help
python -m src.s3_storage --help
```

The intended operational sequence is:

1. Select the source directory and backup identifier.
2. Create the compressed archive.
3. Obtain temporary credentials for the upload role.
4. Upload the object to the encrypted S3 bucket.
5. Record the object key and expected SHA-256 digest.
6. Obtain temporary credentials for the restore role.
7. Download and decrypt the backup object.
8. Extract the archive.
9. Verify the SHA-256 digest.
10. Treat the restore as successful only after verification passes.

Use the [restore runbook](docs/restore-runbook.md) for the recovery procedure.

## Testing

Run the unit tests with:

```bash
python -m pytest -q
```

The test suite covers successful operations and should continue expanding around failure paths, including:

- Archive creation and extraction.
- S3 upload and download calls.
- Missing input files.
- Permission or client errors.
- Empty or corrupted objects.
- SHA-256 mismatch during restore.
- Invalid required configuration.

Recommended quality checks:

```bash
ruff check .
bandit -r src
```

Terraform checks:

```bash
cd infra/backup
terraform fmt -check
terraform validate
```

Integration tests should be isolated from unit tests to avoid unexpected AWS usage and charges.

## Cost considerations

The design is intended to minimize recurring cost by using object storage and optional lifecycle transitions. Actual cost depends on:

- Backup volume and frequency.
- S3 storage class.
- Number and size of restore operations.
- Data transfer.
- KMS request volume.
- Retention and lifecycle configuration.
- Number of stored object versions.

See [docs/cost-model.md](docs/cost-model.md) for the assumptions used by this project.

## Limitations

- The Terraform configuration still requires environment-specific validation and production hardening.
- There is no claim of production readiness.
- Disaster recovery is not fully automated across AWS accounts or regions.
- Key rotation, retention policy, alerting, and audit delivery require further hardening.
- Integration tests should be isolated from unit tests to avoid unexpected AWS charges.
- The current CLI interface may evolve while the project is being developed.
- No automated GitHub Actions pipeline has been configured yet.

## Roadmap

- [ ] Review and harden the Terraform configuration for production use.
- [ ] Add GitHub Actions for tests, linting, Terraform validation, and security checks.
- [ ] Add negative tests for permissions, corruption, and SHA-256 mismatches.
- [ ] Add explicit CLI entry points and complete usage examples.
- [ ] Add structured logging and operational error handling.
- [ ] Add retention, lifecycle, and restore-point selection policies.
- [ ] Add optional cross-region or cross-account disaster recovery.
- [ ] Add CloudWatch metrics and operational alerting.
- [ ] Create a tagged `v0.1.0` development release after validation.

## Project status

This is an educational and portfolio project. It demonstrates the design of an encrypted S3 backup workflow, infrastructure as code with Terraform, isolated access roles, and the engineering decisions needed for safe restoration.

The project is functional as a development reference, but it still requires additional testing, CI automation, observability, and production hardening before use with critical data.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.