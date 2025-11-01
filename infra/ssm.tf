resource "aws_ssm_parameter" "openai_api_key" {
  name        = "/fastapi-app/openai-api-key"
  type        = "SecureString"
  value       = var.openai_api_key
  description = "OpenAI API key for FastAPI app"
}
