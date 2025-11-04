# terraform {
#   backend "s3" {
#     bucket = "jojobucksss"
#     key    = "terraform.tfstate"
#     region = "eu-central-1"
#   }
# }

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

# oder löschen -  Terraform defaults to local state