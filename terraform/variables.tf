variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name used in tags."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the EKS cluster (also used to name the VPC)."
  type        = string
  default     = "ironpulse-eks"
}

variable "cluster_version" {
  description = "Kubernetes version for EKS. Pick one in standard support to avoid extended-support charges."
  type        = string
  default     = "1.35"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC."
  type        = string
  default     = "10.30.0.0/16"
}

variable "availability_zone_count" {
  description = "How many AZs to spread subnets across (minimum 2 for EKS)."
  type        = number
  default     = 2

  validation {
    condition     = var.availability_zone_count >= 2
    error_message = "EKS needs subnets in at least two availability zones."
  }
}

variable "node_instance_types" {
  description = "EC2 instance types for the managed node group. m7i-flex.large (2 vCPU / 8 GiB) is Free Tier eligible, so it also works on AWS Free plan accounts, which reject t3.medium."
  type        = list(string)
  default     = ["m7i-flex.large"]
}

variable "node_desired_size" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 3
}

variable "grant_creator_admin" {
  description = "Give the identity running Terraform cluster-admin. Must be false when running as the AWS root user (EKS rejects root as an access-entry principal)."
  type        = bool
  default     = true
}

variable "create_ci_deployer" {
  description = "Create a least-privilege IAM user (eks:DescribeCluster only) that GitHub Actions and kubectl use, with cluster-admin inside Kubernetes."
  type        = bool
  default     = true
}

variable "ci_deployer_principal_arn" {
  description = "Optional extra IAM user/role ARN to grant cluster-admin via an EKS access entry."
  type        = string
  default     = ""
}
