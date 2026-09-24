output "backup_policy_arn" {
  value = aws_iam_policy.backup.arn
}

output "restore_policy_arn" {
  value = aws_iam_policy.restore.arn
}

output "backup_role_arn" {
  value = aws_iam_role.backup.arn
}

output "restore_role_arn" {
  value = aws_iam_role.restore.arn
}