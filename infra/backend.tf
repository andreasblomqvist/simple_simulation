terraform {
  required_version = ">= 1.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.34"
    }

  }
  backend "s3" {
    bucket         = "shared-infrastructure-terraform-state-staging"
    key            = "simple-sim/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "simplesim-terraform-state-lock"
    encrypt        = true
  }
}


