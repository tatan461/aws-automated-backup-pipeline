# Architecture

## Initial local workflow

```text
Source directory
      |
      v
Compressed tar.gz archive
      |
      v
SHA-256 checksum
      |
      v
Verified restore
```

## Planned AWS workflow

```text
Local backup command
      |
      v
Private S3 bucket with SSE-KMS
      |
      v
S3 Lifecycle transition
      |
      v
Low-cost archival storage
```
