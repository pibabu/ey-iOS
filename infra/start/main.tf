provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "fastapi-app"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}