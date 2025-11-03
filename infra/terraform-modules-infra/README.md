# Terraform Infrastructure Setup Guide

This repository contains the Terraform configuration for setting up infrastructure components including EC2 instances, Parameter Store, and AWS CodePipeline. Below is an overview of each module and the steps to deploy using Terraform.

## EC2 Instance Module
In this module, an EC2 instance is created and configured with the necessary packages using user data. Additionally, a security group is attached to the instance, allowing open access to ports 80 and 443 while restricting port 22 to specific IP addresses for private access.

## Parameter Store Module
The Parameter Store module serves as a simple solution for storing application environment variables (.env file). These secrets can be included during the build pipeline creation process.

## AWS Code Pipeline Module
This module encompasses the creation of a pipeline to deploy changes to the server upon pushing changes to the master branch of the repository. The pipeline includes application and deployment group creation, with the existing EC2 instance added to the deployment group. While auto-scaling groups can be added for scalability, this setup focuses on simplicity by including only one instance in the group.

## Usage
1. Run `terraform init` to download and install modules, and initialize the backend.
2. Use `terraform validate` to check the syntax and configuration of the .tf files.
3. Generate an execution plan using `terraform plan`.
4. Deploy changes to the cloud with `terraform apply`.
To destroy all managed resources, run `terraform destroy`.


For detailed instructions and best practices, please refer to the respective module directories.
