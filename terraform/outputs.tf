output "region" {
  description = "AWS region."
  value       = var.aws_region
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version running on the cluster."
  value       = module.eks.cluster_version
}

output "vpc_id" {
  description = "ID of the VPC."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnets (load balancers, NAT gateway)."
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "Private subnets (worker nodes)."
  value       = module.vpc.private_subnets
}

output "configure_kubectl" {
  description = "Run this to point kubectl at the new cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "ci_deployer_access_key_id" {
  description = "Access key ID for the deployer user (store as the AWS_ACCESS_KEY_ID GitHub secret)."
  value       = var.create_ci_deployer ? aws_iam_access_key.ci_deployer[0].id : null
}

output "ci_deployer_secret_access_key" {
  description = "Secret key for the deployer user (store as AWS_SECRET_ACCESS_KEY). Read with: terraform output -raw ci_deployer_secret_access_key"
  value       = var.create_ci_deployer ? aws_iam_access_key.ci_deployer[0].secret : null
  sensitive   = true
}
