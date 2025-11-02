# ==========================================
# EC2 ROLE
# ==========================================
# AWS IAM Role
resource "aws_iam_role" "ec2_role" {
  name = "${var.app_name}-ec2-role"
  
  # AWS trust policy: WHO can assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"  # EC2 service can use it
      }
    }]
  })
}

# Terraform: Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "ec2_ssm_default" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedEC2InstanceDefaultPolicy"
}

resource "aws_iam_role_policy_attachment" "ec2_ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Custom policy for S3 artifact access
resource "aws_iam_role_policy" "ec2_s3_artifacts" {
  name = "s3-artifacts-access"
  role = aws_iam_role.ec2_role.id
  
  # AWS permissions policy: WHAT this role can do
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        aws_s3_bucket.artifacts.arn,
        "${aws_s3_bucket.artifacts.arn}/*"
      ]
    }]
  })
}

# AWS Instance Profile (wrapper for EC2 to use role)
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.app_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# ==========================================
# CODEDEPLOY ROLE  ehhhhhhhhhhhh
# ==========================================
resource "aws_iam_role" "codedeploy_role" {
  name = "${var.app_name}-codedeploy-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "codedeploy.amazonaws.com"
      }
    }]
  })
}

# AWS managed policy has everything CodeDeploy needs
resource "aws_iam_role_policy_attachment" "codedeploy" {
  role       = aws_iam_role.codedeploy_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRole"
}