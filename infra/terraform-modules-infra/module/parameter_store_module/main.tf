# parameter store
resource "aws_ssm_parameter" "secure_parameter" {
  name        = var.parameter_store_name
  description = "My secure parameter"
  type        = "SecureString"
  value       = "TEST VALUE AFTER DEPLOYMENT"
  tags        = var.tags
}