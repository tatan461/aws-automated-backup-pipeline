output "backup_policy_arn" {
  value = aws_iam_policy.backup.arn
}

output "restore_policy_arn" {
  value = aws_iam_policy.restore.arn
}