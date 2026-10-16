# Rubric evidence map — IronPulse

How each item in the capstone `GRADING.md` maps to this repository, and a command that verifies it. Scope: everything runs locally (Docker Compose and a local Kubernetes cluster) and in GitHub Actions. The AWS Terraform code is included but **not provisioned**.

## M1 — Application (10)

| Criterion | Where | Verify |
|-----------|-------|--------|
| FastAPI `/health` | `backend/app/main.py` | `curl localhost:8000/health` → `{"status":"UP"}` |
| ≥ 4 REST endpoints (GET/POST/PUT/DELETE) | `backend/app/routers/`: 5 resources, 20+ endpoints | http://localhost:8000/docs |
| PostgreSQL tables via Alembic | `backend/alembic/versions/0001_initial_schema.py`, `0002_seed_plans_trainers.py` | `docker compose exec postgres psql -U ironpulse -c '\dt'` |
| React frontend calling the API | `frontend/src/api.js`, `frontend/src/pages/` | http://localhost:3000 |
| Responsive UI | `frontend/src/styles.css` (breakpoints at 1100 / 820 / 520 px) | browser dev-tools device mode; `docs/screenshots/` |

## M2 — Testing (10)

| Criterion | Where | Verify |
|-----------|-------|--------|
| `pytest` passes | `backend/tests/` | `cd backend && pytest -v` → 27 passed |
| ≥ 5 tests over ≥ 3 endpoints | `test_system.py`, `test_plans.py`, `test_trainers.py`, `test_members.py`, `test_checkins_dashboard.py` | same |
| Test DB, not production | `backend/tests/conftest.py`: in-memory SQLite via `app.dependency_overrides[get_db]` | read the fixture |
| `pytest.ini` / `conftest.py` | `backend/pytest.ini`, `backend/tests/conftest.py` | — |

## M3 — Git & GitHub (5)

- Public repo: https://github.com/Himanshu10071/devops-project
- 20+ descriptive commits: `git log --oneline`
- `.gitignore` excludes `.env`, `__pycache__`, `node_modules`, `.venv`, Terraform state and `*.tfvars`

## M4 — Docker (10)

| Criterion | Where | Verify |
|-----------|-------|--------|
| Backend Dockerfile builds | `backend/Dockerfile` (multi-stage) | `docker build ./backend` |
| Frontend multi-stage (Node → Nginx) | `frontend/Dockerfile`: `node:24-alpine` → `nginx-unprivileged` | `docker build ./frontend` |
| Non-root images | uid 10001 (backend), uid 101 (frontend) | `docker compose exec backend id`, `docker compose exec frontend id` |
| Compose starts 3 services | `docker-compose.yml` | `docker compose up --build` then `docker compose ps` |

## M5 — CI/CD (15)

| Criterion | Where |
|-----------|-------|
| Workflow file | `.github/workflows/ci-cd.yml` |
| Triggers on push to `main` | `on.push.branches: [main]` |
| pytest job gates the build | job `test`; `build-scan-push` has `needs: test` |
| Frontend built in pipeline | `npm ci && npm run build` in job `test` |
| Images built for both | step "Build images (tagged with commit SHA)" |
| Pushed to GHCR | step "Push images" → `ghcr.io/himanshu10071/ironpulse-{backend,frontend}` (public) |
| Tags = commit SHA | `:${{ github.sha }}`; no `latest` tag |

Runs: https://github.com/Himanshu10071/devops-project/actions. The `deploy` job is intentionally skipped because no EKS cluster exists (it is gated on the `DEPLOY_ENABLED` variable).

## M6 — DevSecOps / Trivy (5)

The steps "Trivy scan — backend" and "Trivy scan — frontend" use `severity: HIGH,CRITICAL`, `ignore-unfixed: true` and `exit-code: '1'`. The action is pinned to the v0.35.0 commit SHA.

**Explanation:**
> Trivy scanned both container images (the Debian 13 OS packages and Python packages in the backend; the Alpine 3.24 packages in the Nginx frontend) for known CVEs, and the pipeline fails on any HIGH or CRITICAL issue with an available fix. The first backend scan found 4 HIGH vulnerabilities (urllib3 CVE-2026-97687 and CVE-2026-97689, msgpack GHSA-6v7p-g79w-8964, setuptools CVE-2025-47273). All four were inside pip's bundled libraries, not our application dependencies, so I removed pip from the runtime image. Both images now scan clean, which means no known fixable HIGH/CRITICAL vulnerabilities at scan time; it does not mean the images are vulnerability-free.

## M7 — Terraform (15) — code included, not provisioned

| Criterion | Where |
|-----------|-------|
| Valid HCL | `terraform/*.tf`: `terraform init -backend=false && terraform validate` → "Success! The configuration is valid." |
| VPC with ≥ 2 public subnets | `module "vpc"`: 2 public + 2 private subnets across 2 AZs, NAT gateway |
| EKS + node group | `module "eks"`: managed node group `main` (3 × t3.medium, AL2023) |
| No credentials committed | `terraform/terraform.tfvars.example`; `*.tfvars` and state are git-ignored |

`terraform plan`, `apply` and `destroy` were not run, so no AWS resources were created.

## M8 — Kubernetes + Helm (15) — verified on a local cluster

| Criterion | Where | Verify |
|-----------|-------|--------|
| `k8s/namespace.yaml` | restricted Pod Security Standard | `kubectl apply -f k8s/namespace.yaml` |
| Chart with Chart.yaml, values.yaml, templates | `helm/ironpulse/` | `helm lint helm/ironpulse` |
| `helm upgrade --install` works | README → Kubernetes + Helm | `helm list -n ironpulse` |
| ≥ 2 replicas each | `replicaCount: 2` for both, HPA min 2 | `kubectl get deploy -n ironpulse` |
| ClusterIP Services | `templates/backend.yaml`, `templates/frontend.yaml` | `kubectl get svc -n ironpulse` |
| Ingress `/` → frontend, `/api` → backend | `templates/ingress.yaml` (Traefik) | `curl http://ironpulse.local/api/plans` |
| All pods Running | — | `kubectl get pods -n ironpulse` |

The EKS-specific pieces (`values-prod.yaml`, `k8s/storageclass-gp3.yaml`) are included for the AWS path, which was not provisioned.

## M9 — Observability (10) — verified on a local cluster

| Criterion | Where | Verify |
|-----------|-------|--------|
| `/metrics` in Prometheus format | `prometheus-fastapi-instrumentator` + `gym_checkins_total` | `curl localhost:8000/metrics` |
| Prometheus scraping the app | `templates/monitoring.yaml` (ServiceMonitor) + `monitoring/prometheus-values.yaml` | Prometheus → Status → Targets: `ironpulse-backend` UP |
| Grafana installed | kube-prometheus-stack | `kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80` |
| Live panels | "IronPulse — API Overview" dashboard (`helm/ironpulse/dashboards/ironpulse.json`) | run `scripts/load-test.sh`, then open the dashboard |

## M10 — Documentation & presentation (5)

- `README.md` explains the app, every DevOps layer and the project scope.
- `docs/DEMO.md` is the live demo script (commit → pipeline → updated deployment).

---

## Final check before submitting

- [ ] Repo URL submitted (repo is public)
- [ ] Latest Actions run on `main` is green (deploy job shows *skipped*)
- [ ] GHCR packages are public and show SHA tags
- [ ] `docker compose up --build` works on a clean checkout
- [ ] No secrets in history: `git log -p | grep -iE "aws_secret|secret_access_key"` finds nothing beyond placeholders
