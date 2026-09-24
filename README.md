# AWS Automated Backup Pipeline

A cost-conscious backup and restore pipeline built with Python, Boto3, Amazon S3, AWS KMS, Terraform, and configurable lifecycle policies.

## Project status

Early development. The first milestone implements local archive creation, SHA-256 integrity verification, and restore testing before AWS resources are added.

## Goals

- Create compressed backups from a source directory.
- Verify backup integrity with SHA-256 checksums.
- Store encrypted archives in a private S3 bucket.
- Use AWS KMS for server-side encryption.
- Apply lifecycle policies for lower-cost archival storage.
- Provide a tested restore workflow.
- Keep the initial architecture and operating costs intentionally low.

## Repository structure

```text
.
├── src/backup.py                 # Local backup and restore primitives
├── tests/test_backup.py          # Unit tests
├── infra/backup/                 # Terraform AWS infrastructure
├── docs/                         # Architecture and operational documentation
├── examples/sample-data/         # Safe sample data for demonstrations
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Design principles

- No always-on compute for the initial version.
- No NAT Gateway.
- Private S3 storage.
- Configurable retention and lifecycle transitions.
- Explicit integrity verification before restore.
- AWS resources managed with Terraform.

## Planned AWS integration

The next milestone will add S3 upload and download operations, followed by Terraform-managed S3 and KMS resources. Scheduled execution, notifications, and Glacier lifecycle transitions will be added only after the core backup and restore workflow is tested.

## License

MIT License.
