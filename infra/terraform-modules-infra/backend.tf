terraform {
  backend "s3" {
    bucket = "your-project-terraform-file"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}