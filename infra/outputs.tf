output "ec2_public_ip" {
  description = "EC2 public IP"
  value       = aws_instance.app_server.public_ip
}

output "app_url" {
  description = "Application URL"
  value       = "http://${aws_instance.app_server.public_ip}"
}

output "ssh_command" {
  description = "SSH connection command"
  value       = "ssh -i ~/.ssh/${var.ssh_key_name}.pem ec2-user@${aws_instance.app_server.public_ip}"
}

output "codedeploy_role_arn" {
  description = "Use this ARN in AWS Console CodePipeline"
  value       = aws_iam_role.codedeploy_role.arn
}

output "artifacts_bucket" {
  description = "S3 bucket for artifacts"
  value       = aws_s3_bucket.artifacts.id
}