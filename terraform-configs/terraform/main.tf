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

resource "aws_instance" "app_server" {
  ami                     = "ami-0fcf52bcf5db7b003"
  instance_type           = "t2.medium"
  user_data               = data.template_file.user_data.rendered
  security_groups         = ["qgis-tiles"]
  key_name                = var.key_name
  vpc_security_group_ids  = ["sg-08bbc6f92e21ae2d8"]

  tags = {
    Name = var.instance_name
  }
}

resource "aws_ebs_volume" "qgis-tiles" {
  availability_zone = "us-west-2"
  size              = 200
  tags = {
    Name = "qgis-tiles"
  }
}