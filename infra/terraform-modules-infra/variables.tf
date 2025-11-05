variable "aws_region" {
  type        = string
  description = "AWS region where resources will be provisioned"
  default     = "eu-central-1" 
}

# ----------------------------------------------------------------
# ---------------------- AWS Resource Tags -----------------------
# ----------------------------------------------------------------


# variable "ssh_allowed_ip" {
#   type    = string
#   default = "88.72.142.87/32"
# }


# ------------------    VPC    -----------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zone" {
  description = "Availability zone"
  type        = string
  default     = "eu-central-1a"
}



# ----------------------------------------------------------------
# ---------------------- AWS Resource Tags -----------------------
# ----------------------------------------------------------------



variable "project_name" {
  type    = string
  default = "xx"
}

variable "environment" {
  type    = string
  default = "Production"
}

variable "account_id" {
  type    = string
  default = "366101697591"
}

variable "codepipeline_s3_bucket" {
  description = "S3 bucket name for CodePipeline artifacts"
  type        = string
  default     = "codepipeline-eu-central-1-fdd7ab796ddd-49eb-9554-347fb077325a"
}

# ----------------------------------------------------------------
# # --------------- AWS PARAMETER STORE VARIABLES ------------------
# # ----------------------------------------------------------------

# variable "parameter_store_name" {
#   type        = string
#   description = "Name of the AWS SSM Parameter Store"
#   default     = "/project/be"
# }

# # ----------------------------------------------------------------
# --------------- AWS CodePipeline VARIABLES ---------------------
# ----------------------------------------------------------------

# variable "FullRepositoryId" {
#   type        = string
#   description = "Repository used in code pipeline"
#   default     = "rafay-tariq/ProjectBackend"
# }

# variable "BranchName" {
#   type        = string
#   description = "Select branch from repository "
#   default     = "main"
# }

# variable "s3BucketNameForArtifacts" {
#   type        = string
#   description = "S3 bucket to store the source code artifacts"
#   default     = "example-artifact-bucket-some-more-me-random-meeeee"
# }

# variable "CodeStarConnectionArn" {
#   type        = string
#   description = "Existing connection of github/bitbucket with AWS Coestart"
#   default     = "arn:aws:codestar-connections:us-east-1:553723657971:connection/99b23235-d2be-482b-b00c-c449716f1cde"
# }
