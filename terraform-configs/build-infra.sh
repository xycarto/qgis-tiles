#!/bin/bash

## Example for single run
cd terraform-configs

cp -r terraform terraform-tiles

cd terraform-tiles

terraform init 

terraform apply -auto-approve

terraform validate

# Add instance description and test here
echo "Waiting to initialize..."
aws ec2 wait instance-status-ok --region "us-west-2" --instance-ids $(terraform output -raw instance_id) 

echo "Copy creds..."
scp -o StrictHostKeyChecking=no -i ${key} -r ../../.creds ubuntu@$(terraform output -raw instance_public_ip):/home/ubuntu/

echo "Copy scripts..."
scp -o StrictHostKeyChecking=no -i ${key}  -r ../build.sh ubuntu@$(terraform output -raw instance_public_ip):/home/ubuntu/

echo "Running process command..."
ssh -o StrictHostKeyChecking=no -i ${key}  ubuntu@$(terraform output -raw instance_public_ip) "bash build.sh"

terraform destroy -auto-approve

cd ../

rm -rf terraform-tiles