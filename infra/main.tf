terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "infra-state-eyios"
    key    = "terraform.tfstate"
    region = "eu-central-1"
  }
}

provider "aws" {
  region = var.region
}

# Load order: IAM first, then SSM, then EC2.
module "iam" {
  source = "./"
}

module "ssm" {
  source = "./"
  depends_on = [module.iam]
}

module "ec2" {
  source = "./"
  depends_on = [module.ssm]
}
