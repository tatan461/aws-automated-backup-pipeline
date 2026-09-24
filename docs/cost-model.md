# Cost Model

The initial version uses local execution and does not require always-on AWS compute. Planned AWS costs are primarily S3 storage, S3 requests, KMS usage, and archival retrieval when applicable.

Lifecycle transitions and retention periods must account for minimum storage durations and retrieval charges. Test with small sample archives and configure AWS Budgets before production use.
