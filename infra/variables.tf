variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-central-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "ec2_key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "domain_name" {
  description = "Application domain"
  type        = string
  default     = "ey-ios.com"
}

variable "app_port" {
  description = "Port FastAPI runs on"
  type        = number
  default     = 8000
}

variable "openai_api_key" {
  description = "Your OpenAI API key to be stored in SSM"
  type        = string
  sensitive   = true
}
