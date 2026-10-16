#!/usr/bin/env bash
# One-time cluster add-ons for IronPulse: Traefik ingress controller, metrics-server (for HPA),
# Prometheus + Grafana, and (on EKS) a default gp3 StorageClass.
#
# Usage:  ./scripts/bootstrap-cluster.sh          # EKS
#         ./scripts/bootstrap-cluster.sh --local  # Docker Desktop / minikube / kind
set -euo pipefail
cd "$(dirname "$0")/.."

LOCAL=false
[[ "${1:-}" == "--local" ]] && LOCAL=true

echo "==> Helm repositories"
helm repo add traefik https://traefik.github.io/charts >/dev/null
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ >/dev/null
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null

echo "==> Namespace"
kubectl apply -f k8s/namespace.yaml

if [[ "$LOCAL" == false ]]; then
  echo "==> gp3 default StorageClass (EKS)"
  kubectl apply -f k8s/storageclass-gp3.yaml
  # Remove the default flag from the legacy gp2 class if present.
  kubectl annotate storageclass gp2 storageclass.kubernetes.io/is-default-class- 2>/dev/null || true
fi

# Traefik implements the standard Ingress resource (ingress-nginx was retired in March 2026).
echo "==> Traefik ingress controller (Service type LoadBalancer -> AWS load balancer on EKS)"
helm upgrade --install traefik traefik/traefik \
  -n traefik --create-namespace \
  --set ingressClass.enabled=true \
  --set ingressClass.isDefaultClass=true \
  --set providers.kubernetesIngress.publishedService.enabled=true \
  --wait

echo "==> metrics-server (HPA needs CPU metrics)"
METRICS_ARGS=()
[[ "$LOCAL" == true ]] && METRICS_ARGS=(--set "args={--kubelet-insecure-tls}")
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system "${METRICS_ARGS[@]}" --wait

echo "==> kube-prometheus-stack (Prometheus + Grafana)"
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml --wait --timeout 10m

echo
echo "Cluster ready. Deploy the app with:"
if [[ "$LOCAL" == true ]]; then
  echo "  helm upgrade --install ironpulse ./helm/ironpulse -n ironpulse -f helm/ironpulse/values-dev.yaml"
else
  echo "  helm upgrade --install ironpulse ./helm/ironpulse -n ironpulse -f helm/ironpulse/values-prod.yaml --set backend.image.tag=<sha> --set frontend.image.tag=<sha>"
fi
echo "Ingress address:"
kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0]}{"\n"}' || true
