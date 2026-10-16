terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.95, < 6.0"
    }
  }

  # Optional remote state (recommended for teams). Create the bucket first, then
  # uncomment and run `terraform init -migrate-state`.
  # backend "s3" {
  #   bucket       = "ironpulse-tfstate-<your-account-id>"
  #   key          = "eks/terraform.tfstate"
  #   region       = "ap-south-1"
  #   use_lockfile = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ironpulse"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
