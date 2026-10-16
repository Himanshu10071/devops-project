# Live demo script (about 15 minutes, all local)

The demo runs on your laptop: Docker Compose for the app, a local Kubernetes cluster (Docker Desktop Kubernetes or kind) for Helm, Ingress, HPA and monitoring, and GitHub for CI. AWS is shown as code only.

**Before the demo:**
1. `docker compose up -d --build`, then `URL=http://localhost:3000 ./scripts/seed-demo-data.sh`
2. Start the local cluster, run `./scripts/bootstrap-cluster.sh --local`, then deploy the chart (README → Kubernetes + Helm).
3. Open tabs: http://localhost:3000, http://localhost:8000/docs, the GitHub Actions page, the GHCR packages page, Grafana and Prometheus (port-forwards from the README).
4. Run `scripts/load-test.sh` for a minute so Grafana has data.

| # | Show | How |
|---|------|-----|
| 1 | **Application** | http://localhost:3000 → Dashboard. Register a member, check them in, watch the KPIs update. Freeze a member and show that check-in is refused. |
| 2 | **API** | `/docs` → `POST /api/plans`, `GET /api/members?state=EXPIRING_SOON`, `PUT`, `DELETE`. |
| 3 | **Database** | `docker compose exec postgres psql -U ironpulse -c "select full_name, end_date from members;"` |
| 4 | **Tests** | `cd backend && pytest -v` (27 passed, isolated SQLite DB). |
| 5 | **Git** | Change something visible, e.g. the subtitle in `frontend/src/pages/Dashboard.jsx`. Then `git commit -am "Update dashboard greeting copy" && git push`. |
| 6 | **CI** | Actions tab: the test job (pytest + frontend build), then build-scan-push. The deploy job is *skipped*: no cloud cluster. |
| 7 | **Docker** | Build step: two images tagged with the commit SHA. Locally: `docker compose ps`, `docker compose exec backend id` (non-root). |
| 8 | **Security** | Expand the Trivy steps and explain the pip finding (README → Security). |
| 9 | **Registry** | GHCR packages page: the new SHA tag, public. |
| 10 | **Terraform** | Walk through `terraform/main.tf` (VPC module → EKS module → EBS CSI IRSA) and run `terraform validate`. Explain that it is not provisioned, to avoid AWS cost. |
| 11 | **Kubernetes** | `kubectl get pods,svc -n ironpulse`: 2 backend, 2 frontend, 1 postgres, all Running. |
| 12 | **Helm** | `helm list -n ironpulse`, then `helm history ironpulse -n ironpulse`. Deploy the new SHA with `helm upgrade … --set backend.image.tag=<new sha> --set frontend.image.tag=<new sha>` and show a new revision; mention `helm rollback`. |
| 13 | **Ingress** | http://ironpulse.local: your change is live. `kubectl get ingress -n ironpulse`: `/api` → backend, `/` → frontend. |
| 14 | **HPA** | `kubectl get hpa -n ironpulse -w` while running `URL=http://ironpulse.local ./scripts/load-test.sh 120 25`: replicas go 2 → 6. |
| 15 | **Monitoring** | Prometheus → Status → Targets (backend UP). Grafana → "IronPulse — API Overview": request rate, p95 latency, check-ins, CPU, replicas. |
| 16 | **Failure** | `kubectl apply -f troubleshooting/broken-service.yaml` → `kubectl get endpoints -n ironpulse` shows `<none>` → fix the selector (`troubleshooting/README.md`). |

## One-liners for questions

- **Why `/health` *and* `/ready`?** Liveness restarts a hung process; readiness only removes the pod from load balancing while the DB is unavailable, so a DB blip doesn't cause a restart storm.
- **Why SHA tags?** They're immutable and traceable to a commit, which makes deploys reproducible and rollbacks exact. `latest` is neither.
- **Why tests before images?** Broken code never reaches the registry, so it can't be deployed.
- **Why isn't it on AWS?** The Terraform is complete and validated, but EKS and NAT gateways are billed hourly; the same Helm chart is proven on a local cluster.
- **Postgres in Kubernetes vs RDS?** In-cluster is fine for a demo. In production, RDS gives backups, Multi-AZ failover and patching; the chart supports it with `postgres.enabled=false` and `postgres.externalHost`.
- **Ingress vs Ingress Controller?** The Ingress is only routing rules; Traefik is the controller that implements them.
