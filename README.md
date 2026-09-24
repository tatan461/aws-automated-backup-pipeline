<h1 align="center">AWS Automated Backup Pipeline</h1>

<p align="center">
  Secure, encrypted, and integrity-verified backup and restore workflow built with AWS, Python, and Terraform.
</p>

<p align="center">
  <a href="https://aws.amazon.com/">
    <img src="https://img.shields.io/badge/Cloud-AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=FF9900" alt="AWS">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://registry.terraform.io/">
    <img src="https://img.shields.io/badge/Infrastructure-Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white" alt="Terraform">
  </a>
  <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/index.html">
    <img src="https://img.shields.io/badge/AWS%20SDK-Boto3-FF9900?style=flat-square&logo=amazonaws&logoColor=white" alt="Boto3">
  </a>
</p>

<p align="center">
  <a href="https://github.com/tatan461/aws-automated-backup-pipeline">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub repository">
  </a>
  <a href="https://www.linkedin.com/in/jonathan-angel-gonzalez-0543b441a/">
    <img src="https://img.shields.io/badge/LinkedIn-Profile-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn profile">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-2EA44F?style=flat-square" alt="MIT License">
  </a>
</p>

---

## Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Security](#security)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Infrastructure](#infrastructure)
- [Testing](#testing)
- [Documentation](#documentation)
- [Author](#author)
- [License](#license)

## Overview

This project implements a secure backup and restore workflow using Amazon S3, AWS KMS, IAM roles, STS temporary credentials, Python, and Terraform.

The pipeline:

1. Packages a local directory into a `tar.gz` archive.
2. Uploads the backup to Amazon S3.
3. Encrypts the object with AWS KMS.
4. Restores the object through a separate read/decrypt workflow.
5. Verifies the restored data using SHA-256.

The architecture separates upload and restore permissions to follow least-privilege principles.

## Architecture

<p align="center">
  <img src="docs/architecture.png" alt="AWS Automated Backup Pipeline architecture">
</p>

```text
Source directory
    -> Python CLI creates archive
    -> Upload role writes to S3
    -> S3 encrypts the object with KMS
    -> Restore role reads and decrypts the object
    -> Python CLI verifies SHA-256
    -> Restored files
```

## Technology stack

| Component | Purpose |
|---|---|
| Python CLI | Creates archives and verifies restored data |
| Amazon S3 | Stores encrypted backup objects |
| AWS KMS | Provides server-side encryption |
| AWS IAM | Separates upload and restore permissions |
| AWS STS | Provides temporary credentials |
| Terraform | Provisions the AWS infrastructure |
| SHA-256 | Verifies backup integrity after restore |

## Security

- S3 public access is blocked.
- Backup objects use SSE-KMS encryption.
- Upload and restore access are isolated through separate IAM roles.
- Temporary STS credentials are preferred over long-lived access keys.
- Terraform variables and state files must remain outside version control.
- SHA-256 verification detects corrupted or incomplete restores.

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

## Requirements

- Python 3.11+
- Terraform 1.5+
- AWS CLI
- An AWS account for deployment or integration testing

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

## Infrastructure

Terraform configuration is located in `infra/backup/`.

The configuration provisions and manages:

- An Amazon S3 backup bucket.
- Server-side encryption with AWS KMS.
- S3 versioning.
- Public-access blocking.
- Lifecycle configuration.
- Example deployment variables.

The example variables file is provided for reference. Create a local `terraform.tfvars` file and review all values before deployment.

```bash
cd infra/backup

cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

Review the Terraform plan before applying it.

Never commit:

- `terraform.tfvars`
- AWS credentials
- Terraform state files
- `.env` files

## Testing

Run the unit tests with:

```bash
python -m pytest -q
```

Optional quality checks:

```bash
ruff check .
bandit -r src
```

Terraform validation:

```bash
cd infra/backup
terraform fmt -check
terraform validate
```

Integration tests should be isolated from unit tests to avoid unexpected AWS usage and charges.

## Documentation

- [Architecture notes](docs/architecture.md)
- [Restore runbook](docs/restore-runbook.md)
- [Cost model](docs/cost-model.md)

## Author

<p align="center">
  <strong>Jonathan Angel Gonzalez</strong><br>
  Junior Cloud Engineer · AWS Certified Specialist
</p>

<p align="center">
  <a href="https://github.com/tatan461">
    <img src="https://img.shields.io/badge/GitHub-@tatan461-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub profile">
  </a>
  <a href="https://www.linkedin.com/in/jonathan-angel-gonzalez-0543b441a/">
    <img src="https://img.shields.io/badge/LinkedIn-Jonathan%20Angel%20Gonzalez-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn profile">
  </a>
</p>

## License

This project is licensed under the [MIT License](LICENSE).