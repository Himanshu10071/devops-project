# Rubric evidence map — IronPulse

Every criterion in the capstone `GRADING.md`, with the files that implement it and the screenshot that proves it. Screenshots are in [`screenshots/`](screenshots/). The AWS run happened on 16 Oct 2026 in `ap-south-1`; the infrastructure was destroyed afterwards.

## M1 — Application (10)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| FastAPI `/health` | `backend/app/main.py` | `m4-compose-ps-nonroot.png` (`curl /health` → UP) |
| ≥ 4 REST endpoints (GET/POST/PUT/DELETE) | `backend/app/routers/`: 5 resources, 20+ endpoints | `m8-app-eks-swagger.png` |
| PostgreSQL + Alembic | `backend/alembic/versions/0001_initial_schema.py`, `0002_seed_plans_trainers.py` | backend start-up runs `alembic upgrade head` |
| React frontend calling the API | `frontend/src/api.js`, `frontend/src/pages/` | `m8-browser-ingress-elb.png`, `app-dashboard.png` |
| Responsive UI | `frontend/src/styles.css` | `app-members-mobile.png`, `app-plans.png` |

## M2 — Testing (10)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| `pytest` passes | `backend/tests/` | `m2-pytest.png` (27 passed) |
| ≥ 5 tests over ≥ 3 endpoints | 5 test modules covering plans, trainers, members, check-ins, dashboard, system | `m2-pytest.png` |
| Test DB, not production | `backend/tests/conftest.py`: in-memory SQLite via `app.dependency_overrides[get_db]` | — |
| `pytest.ini` / `conftest.py` | `backend/pytest.ini`, `backend/tests/conftest.py` | — |

## M3 — Git & GitHub (5)

| Criterion | Evidence |
|-----------|----------|
| Public repo | https://github.com/Himanshu10071/devops-project |
| Meaningful commits (≥ 10) | `m3-github-commits.png`, `m3-git-log.png` |
| `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv` | `.gitignore` (also Terraform state and `*.tfvars`) |

## M4 — Docker (10)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| Backend Dockerfile builds | `backend/Dockerfile` (multi-stage) | `m4-compose-up.png` |
| Frontend multi-stage (Node → Nginx) | `frontend/Dockerfile` | `m4-compose-up.png` |
| Non-root images | uid 10001 / uid 101 | `m4-compose-ps-nonroot.png` |
| Compose starts all 3 services | `docker-compose.yml` | `m4-compose-up.png`, `m4-compose-ps-nonroot.png` |

## M5 — CI/CD (15)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| Workflow file, triggers on push to `main` | `.github/workflows/ci-cd.yml` | `m5-actions-run-deploy.png` |
| pytest gates the build | job `test`; `build-scan-push` has `needs: test` | `m5-actions-run-deploy.png` |
| Frontend built in pipeline | `npm ci && npm run build` | same |
| Both images built | step "Build images (tagged with commit SHA)" | same |
| Pushed to GHCR | `ghcr.io/himanshu10071/ironpulse-{backend,frontend}` (public) | `m5-ghcr-backend.png`, `m5-ghcr-frontend.png` |
| SHA tags, not `latest` | `:${{ github.sha }}` | GHCR pages show 40-character SHA tags |

Successful run with deploy: https://github.com/Himanshu10071/devops-project/actions/runs/38945078958

## M6 — DevSecOps / Trivy (5)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| Trivy on both images | steps "Trivy scan — backend/frontend" | `m6-trivy-backend.png`, `m6-trivy-frontend.png` |
| Fails on HIGH/CRITICAL | `severity: HIGH,CRITICAL`, `exit-code: '1'` | workflow file |
| Explain a CVE / clean result | below | — |

**Explanation:**
> Trivy scanned both container images (the Debian 13 OS packages and Python packages in the backend; the Alpine 3.24 packages in the Nginx frontend) for known CVEs, and the pipeline fails on any HIGH or CRITICAL issue with an available fix. The first backend scan found 4 HIGH vulnerabilities (urllib3 CVE-2026-97687 and CVE-2026-97689, msgpack GHSA-6v7p-g79w-8964, setuptools CVE-2025-47273). All four were inside pip's bundled libraries, not our application dependencies, so I removed pip from the runtime image. Both images now scan clean, which means no known fixable HIGH/CRITICAL vulnerabilities at scan time; it does not mean the images are vulnerability-free.

## M7 — Terraform (15)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| Valid HCL | `terraform/*.tf` | `m7-terraform-plan.png` |
| `terraform init` | — | ran clean before plan |
| `terraform plan` non-empty, no errors | — | `m7-terraform-plan.png` (Plan: 64 to add) |
| VPC with ≥ 2 public subnets | `module "vpc"` | `m7-console-vpc.png`, `m7-console-subnets.png`, `m7-aws-vpc-cli.png` (public → IGW, private → NAT) |
| EKS + ≥ 1 node group | `module "eks"` | `m7-console-eks-cluster.png`, `m7-console-eks-nodegroup.png`, `m7-aws-eks-cli.png` |
| `terraform destroy` clean | — | `m7-terraform-destroy.png`, `m7-aws-after-destroy.png` |
| `terraform.tfvars.example`, no credentials | `terraform/terraform.tfvars.example` | `*.tfvars` and state are git-ignored |

## M8 — Kubernetes + Helm (15)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| `k8s/namespace.yaml` applies | restricted Pod Security | `m8-helm-list-history.png` (`namespace/ironpulse unchanged`) |
| Chart with Chart.yaml, values.yaml, templates | `helm/ironpulse/` | — |
| `helm upgrade --install` works | CI deploy job + manual install | `m8-helm-list-history.png`, `m5-actions-run-deploy.png` |
| ≥ 2 replicas each | `replicaCount: 2`, HPA min 2 | `m8-kubectl-pods.png` |
| ClusterIP Services | `templates/backend.yaml`, `templates/frontend.yaml` | `m8-kubectl-svc-ingress-hpa.png` |
| Ingress `/` → frontend, `/api` → backend | `templates/ingress.yaml` (Traefik) | `m8-kubectl-svc-ingress-hpa.png`, `m8-browser-ingress-elb.png`, `m8-app-eks-swagger.png` |
| All pods Running | — | `m8-kubectl-pods.png` |
| Extra: HPA, rollback, troubleshooting | — | `m8-hpa-scaling.png`, `m8-helm-rollback.png`, `m8-troubleshooting.png` |

## M9 — Observability (10)

| Criterion | Where | Evidence |
|-----------|-------|----------|
| `/metrics` in Prometheus format | `backend/app/main.py`, `routers/checkins.py` | `m9-metrics.png` |
| Prometheus scraping the app | ServiceMonitor in `templates/monitoring.yaml` | `m9-prometheus-targets.png` (3/3 UP) |
| Grafana installed | kube-prometheus-stack, `monitoring/prometheus-values.yaml` | `m9-grafana-dashboard.png` |
| Live panel (requests / latency / errors) | `helm/ironpulse/dashboards/ironpulse.json` | `m9-grafana-dashboard.png` |

## M10 — Documentation & presentation (5)

- `README.md`: the app, every DevOps layer, results and incidents.
- `docs/DEMO.md`: the presentation script, including the commit → pipeline → deployment walkthrough with the recorded EKS run.

---

## Final check before submitting

- [x] Repo is public
- [x] Green Actions runs on `main` (deploy job verified on EKS, now *skipped*)
- [x] GHCR packages public with SHA tags
- [x] All screenshots in `docs/screenshots/`
- [x] `terraform destroy` completed, nothing left running in AWS
- [x] No secrets in Git (the deployer key lived only in GitHub Secrets and was deleted with the IAM user)
