provider "aws" {
  region = var.aws_region
}

locals {
  common_tags = {
    Project_Name = var.project_name
    Environment  = var.environment
    Account_ID   = var.account_id
    Region       = var.aws_region
  }
}

module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr             = var.vpc_cidr
  availability_zone    = var.availability_zone
  tags                 = var.tags
}


module "ec2" {
  source = "./modules/ec2"
  
  vpc_id               = module.vpc.vpc_id
  subnet_id            = module.vpc.public_subnet_id
  
  ami                  = var.ami
  instance_type        = var.instance_type
  instance_name        = var.instance_name
  ec2_role_permissions = var.ec2_role_permissions
  codepipeline_s3_bucket = var.codepipeline_s3_bucket  
  security_group_allowed_ports = var.security_group_allowed_ports
  tags                 = var.tags
}
# module "parameter_store_module" {
#   source               = "./module/parameter_store_module"
#   parameter_store_name = var.parameter_store_name
#   tags                 = local.common_tags
#  }

# module "code_pipeline_module" {
#   source                   = "./module/code_pipeline_module"
#   instance_name            = module.ec2_instance_module.instance_details.instance_name
#   FullRepositoryId         = var.FullRepositoryId
#   BranchName               = var.BranchName
#   CodeStarConnectionArn    = var.CodeStarConnectionArn
#   s3BucketNameForArtifacts = var.s3BucketNameForArtifacts
#   tags                     = local.common_tags
# }




# ----------------------------------------------------------------
# ---------------------- OUTPUT SECTION --------------------------
# ----------------------------------------------------------------


# # output "parameter_store_name" {
# #   value = module.parameter_store_module.parameter_store_name
# }
output "module_ec2_instance_details" {
  value = module.ec2_instance_module.instance_details
}
output "ec2_instance_ssh_details" {
  value = "ssh -i \"private-key.pem\" ec2-user@${module.ec2_instance_module.elastic_ip}.compute-1.amazonaws.com"
}
