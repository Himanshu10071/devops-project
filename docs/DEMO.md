# Presentation script (about 15 minutes)

The AWS cluster was destroyed after the recorded run to stop the costs, so the demo has two parts. You show the **live** parts on your laptop (app, tests, Git push, CI), and the **AWS run** through the screenshots in `docs/screenshots/`. If the examiner wants AWS live, re-create it with `terraform apply` (~20 min) the day before, then destroy it again.

**Before the demo:**
1. `docker compose up -d --build`, then `URL=http://localhost:3000 ./scripts/seed-demo-data.sh`
2. Open tabs: http://localhost:3000, http://localhost:8000/docs, the GitHub repo, the Actions page and the GHCR packages page.
3. Open `docs/screenshots/` in an image viewer, sorted by name (m1 … m9).

| # | Show | How |
|---|------|-----|
| 1 | **Application** (live) | http://localhost:3000. Register a member, check them in, watch the KPIs update. Freeze the member and show that check-in is refused. |
| 2 | **API** (live) | `/docs`: `POST /api/plans`, `GET /api/members?state=EXPIRING_SOON`, `PUT`, `DELETE`. |
| 3 | **Database** (live) | `docker compose exec postgres psql -U ironpulse -c "select full_name, end_date from members;"` |
| 4 | **Tests** (live) | `cd backend && pytest -v`: 27 passed on an isolated SQLite DB. |
| 5 | **Git + CI** (live) | Change some text, `git commit -am "…" && git push`. On the Actions tab, test → build → Trivy → GHCR all run; deploy is skipped because the cluster is gone. |
| 6 | **Docker** | `docker compose ps`, `docker compose exec backend id` (non-root); `m4-*.png`. |
| 7 | **Security** | Expand a Trivy step in the run (or `m6-*.png`) and explain the pip finding. |
| 8 | **Registry** | GHCR packages page: the new SHA tag, public. |
| 9 | **Terraform** | Walk through `terraform/main.tf` (VPC → EKS → EBS CSI → deployer user). Show `m7-terraform-plan.png` (64 resources), the console screenshots (VPC, subnets, EKS, node group), then `m7-terraform-destroy.png`. |
| 10 | **CI deploy to EKS** | `m5-actions-run-deploy.png` (all 3 jobs green) and `m8-browser-ingress-elb.png`: the subtitle change from that commit live on the AWS load balancer URL. |
| 11 | **Kubernetes + Helm** | `m8-kubectl-pods.png` (2+2 pods across two AZs, SHA images), `m8-kubectl-svc-ingress-hpa.png`, `m8-helm-list-history.png`. |
| 12 | **Failure + rollback** | `m8-helm-rollback.png`. A deploy broke on an empty DB password; the old pods kept serving, `helm rollback` restored it, then the bug was fixed in the workflow and the chart (README → "What went wrong"). |
| 13 | **HPA** | `m8-hpa-scaling.png`: CPU 99% → replicas 2 → 4 → 3. |
| 14 | **Monitoring** | `m9-prometheus-targets.png` (3/3 UP), `m9-grafana-dashboard.png` (traffic spike, latency, CPU, replicas), `m9-metrics.png`. |
| 15 | **Troubleshooting** | `m8-troubleshooting.png`: ImagePullBackOff, a Service with no endpoints fixed to 2 endpoints, CrashLoopBackOff. Live alternative: `kind create cluster` + `bootstrap-cluster.sh --local` + `values-dev.yaml`. |

## One-liners for questions

- **Why `/health` *and* `/ready`?** Liveness restarts a hung process; readiness only removes the pod from load balancing while the DB is unavailable, so a DB blip doesn't cause a restart storm.
- **Why SHA tags?** They're immutable and traceable to a commit, which makes deploys reproducible and rollbacks exact. `latest` is neither.
- **Why tests before images?** Broken code never reaches the registry, so it can't be deployed.
- **Why a separate deployer IAM user?** CI only needs to find the cluster (`eks:DescribeCluster`) and talk to Kubernetes. It never needs AWS admin rights, so a leaked CI key can't touch the rest of the account.
- **Why destroy the cluster?** EKS, the NAT gateway and nodes are billed hourly. Infrastructure as Code means it can be re-created identically with one command.
- **Postgres in Kubernetes vs RDS?** In-cluster is fine for a demo. In production, RDS gives backups, Multi-AZ failover and patching; the chart supports it with `postgres.enabled=false` and `postgres.externalHost`.
- **Ingress vs Ingress Controller?** The Ingress is only routing rules; Traefik is the controller that implements them.
