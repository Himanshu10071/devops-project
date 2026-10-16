# Least-privilege identity for deployments (GitHub Actions + local kubectl).
# AWS side: it may only describe this cluster (enough for `aws eks update-kubeconfig`).
# Kubernetes side: cluster-admin through the EKS access entry in main.tf.
resource "aws_iam_user" "ci_deployer" {
  count = var.create_ci_deployer ? 1 : 0
  name  = "${var.cluster_name}-ci-deployer"
}

resource "aws_iam_user_policy" "ci_deployer_eks" {
  count = var.create_ci_deployer ? 1 : 0
  name  = "eks-describe-cluster"
  user  = aws_iam_user.ci_deployer[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["eks:DescribeCluster", "eks:ListClusters"]
      Resource = "*"
    }]
  })
}

# The secret ends up in the (git-ignored, local) Terraform state; it is deleted on destroy.
resource "aws_iam_access_key" "ci_deployer" {
  count = var.create_ci_deployer ? 1 : 0
  user  = aws_iam_user.ci_deployer[0].name
}
