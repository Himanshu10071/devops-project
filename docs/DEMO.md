# Live demo script (about 15 minutes)

Run this order in the presentation. Commands assume the EKS cluster is up, `bootstrap-cluster.sh` has run and the latest commit is deployed.

**Before the demo:** open tabs for the app (Ingress URL), `/docs`, the GitHub Actions page, the GHCR packages page, Grafana (port-forward) and Prometheus targets (port-forward). Run `scripts/load-test.sh` for a minute so Grafana has data.

| # | Show | How |
|---|------|-----|
| 1 | **Application** | Open the Ingress URL → Dashboard. Register a member, check them in, watch the KPIs update. Freeze a member and show that check-in is refused. |
| 2 | **API** | `/docs` → `POST /api/plans`, `GET /api/members?state=EXPIRING_SOON`, `PUT`, `DELETE`. |
| 3 | **Database** | `kubectl exec -n ironpulse ironpulse-postgres-0 -- psql -U ironpulse -d ironpulse -c "select full_name, end_date from members;"` |
| 4 | **Git** | Change something visible, e.g. the subtitle in `frontend/src/pages/Dashboard.jsx`. Then `git commit -am "Update dashboard greeting copy" && git push`. |
| 5 | **CI** | Actions tab: test job running pytest (27 tests) and the frontend build. |
| 6 | **Docker** | Build job: two images built and tagged with the commit SHA. |
| 7 | **Security** | Expand the Trivy step and explain the pip finding (README → Security). |
| 8 | **Registry** | GHCR packages page: the new SHA tag. |
| 9 | **Terraform** | Walk through `terraform/main.tf` (VPC module → EKS module → EBS CSI IRSA). Show the AWS console VPC + EKS. |
| 10 | **Kubernetes** | `kubectl get pods,svc -n ironpulse -o wide`: pods spread over nodes. |
| 11 | **Helm** | `helm list -n ironpulse`, then `helm history ironpulse -n ironpulse`: a new revision per deploy. Mention `helm rollback`. |
| 12 | **Ingress** | Refresh the app: your change is live. `kubectl get ingress -n ironpulse`. |
| 13 | **HPA** | `kubectl get hpa -n ironpulse -w` while running `URL=http://<lb> ./scripts/load-test.sh 120 40`: replicas go 2 → 3+. |
| 14 | **Monitoring** | Prometheus → Status → Targets (backend UP). Grafana → "IronPulse — API Overview": request rate, p95 latency, check-ins, CPU, replicas. |
| 15 | **Failure** | `kubectl apply -f troubleshooting/broken-service.yaml` → `kubectl get endpoints` shows `<none>` → fix the selector (see `troubleshooting/README.md`). |

## One-liners for questions

- **Why `/health` *and* `/ready`?** Liveness restarts a hung process; readiness only removes the pod from load balancing while the DB is unavailable, so a DB blip doesn't cause a restart storm.
- **Why SHA tags?** They're immutable and traceable to a commit, which makes deploys reproducible and rollbacks exact. `latest` is neither.
- **Why tests before images?** Broken code never reaches the registry, so it can't be deployed.
- **Postgres in Kubernetes vs RDS?** In-cluster is fine for a demo. In production, RDS gives backups, Multi-AZ failover and patching; the chart supports it with `postgres.enabled=false` and `postgres.externalHost`.
- **Ingress vs Ingress Controller?** The Ingress is only routing rules; Traefik is the controller that implements them.
