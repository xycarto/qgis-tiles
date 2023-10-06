terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-west-2"
}

data "template_file" "user_data" {
  template = file("../cloud-init.yml")
}

resource "aws_instance" "qgis_tiles" {
  ami                     = "ami-03f65b8614a860c29"
  instance_type           = "c5a.8xlarge"
  user_data               = data.template_file.user_data.rendered
  security_groups         = ["qgis-tiles"]
  key_name                = var.key_name
  vpc_security_group_ids  = ["sg-08bbc6f92e21ae2d8"]

  # root disk
  root_block_device {
    volume_size           = "200"
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = var.instance_name
  }
}

# resource "root_block_device" "qgis-tiles" {
#   availability_zone = "us-west-2a"
#   size              = 200
#   tags = {
#     Name = "qgis-tiles"
#   }
# }