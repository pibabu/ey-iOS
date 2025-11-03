#!/bin/bash
# set -e: If any command in the script fails (exits with a non-zero status), the shell will terminate the script immediately.
set -e

# Install the CodeDeploy agent
sudo yum update -y
yum install -y ruby
wget https://aws-codedeploy-us-east-1.s3.amazonaws.com/latest/install
chmod +x ./install
./install auto

service codedeploy-agent start
chkconfig codedeploy-agent on

#install the docker 
yum install -y docker
service docker start
chkconfig docker on
usermod -aG docker ec2-user

#install docker compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# install caddy_data volume
docker volume create caddy_data

