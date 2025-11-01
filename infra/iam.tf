resource "aws_iam_role" "fastapi_role" {
  name = "fastapi-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Managed policy for SSM agent + EC2 basic ops
resource "aws_iam_role_policy_attachment" "ssm_managed" {
  role       = aws_iam_role.fastapi_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Allow EC2 to read specific SSM parameters
resource "aws_iam_policy" "fastapi_ssm_policy" {
  name        = "fastapi-ssm-read"
  description = "Allow read access to FastAPI app parameters"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:ssm:${var.region}:*:parameter/fastapi-app/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_custom" {
  role       = aws_iam_role.fastapi_role.name
  policy_arn = aws_iam_policy.fastapi_ssm_policy.arn
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "fastapi_profile" {
  name = "fastapi-instance-profile"
  role = aws_iam_role.fastapi_role.name
}
