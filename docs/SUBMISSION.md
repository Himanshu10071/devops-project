# Submission checklist — IronPulse

How each rubric item in `GRADING.md` maps to this repository, plus the evidence (screenshots) to capture. Save screenshots in `docs/screenshots/` using the file names below.

## M1 — Application (10)

| Criterion | Where |
|-----------|-------|
| FastAPI `/health` | `backend/app/main.py` |
| ≥ 4 REST endpoints (GET/POST/PUT/DELETE) | `backend/app/routers/`: 5 resources, 20+ endpoints |
| PostgreSQL tables via Alembic | `backend/alembic/versions/0001_initial_schema.py`, `0002_seed_plans_trainers.py` |
| React frontend calling the API | `frontend/src/api.js`, `frontend/src/pages/` |
| Responsive UI | `frontend/src/styles.css` (breakpoints at 1100 / 820 / 520 px) |

📸 `m1-dashboard.png`, `m1-members.png`, `m1-mobile.png` (browser dev-tools device mode)

## M2 — Testing (10)

| Criterion | Where |
|-----------|-------|
| `pytest` passes | `cd backend && pytest -v` (27 tests) |
| ≥ 5 tests over ≥ 3 endpoints | `backend/tests/test_*.py` |
| Test DB, not production | `backend/tests/conftest.py`: in-memory SQLite via `dependency_overrides` |
| `pytest.ini` / `conftest.py` | `backend/pytest.ini`, `backend/tests/conftest.py` |

📸 `m2-pytest.png`: terminal output of `pytest -v`

## M3 — Git & GitHub (5)

📸 `m3-commits.png`: `git log --oneline` or the GitHub commits page (20+ descriptive commits). `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv`, Terraform state and tfvars.

## M4 — Docker (10)

| Criterion | Where |
|-----------|-------|
| Backend Dockerfile | `backend/Dockerfile` (multi-stage, uid 10001) |
| Frontend multi-stage (Node → Nginx) | `frontend/Dockerfile` (node:24-alpine → nginx-unprivileged, uid 101) |
| Non-root | both: verify with `docker compose exec backend id` / `docker compose exec frontend id` |
| `docker compose up --build` → 3 services | `docker-compose.yml` |

📸 `m4-compose-up.png`, `m4-localhost-3000.png`

## M5 — CI/CD (15)

`.github/workflows/ci-cd.yml`: triggers on push to `main`; pytest job gates the build; frontend build; both images built; pushed to GHCR; tags = `${{ github.sha }}`.

📸 `m5-actions-green.png` (Actions run page), `m5-ghcr-packages.png` (Profile → Packages, showing SHA tags)

## M6 — Trivy (5)

Scan steps in the workflow (`Trivy scan — backend/frontend`), `exit-code: 1` on `HIGH,CRITICAL`.

📸 `m6-trivy.png`: expand the Trivy step in the Actions log

**Written explanation (paste into the form):**
> Trivy scanned both container images (the Debian 13 OS packages and Python packages in the backend; the Alpine 3.24 packages in the Nginx frontend) for known CVEs, and the pipeline fails on any HIGH or CRITICAL issue with an available fix. The first backend scan found 4 HIGH vulnerabilities (urllib3 CVE-2026-97687 and CVE-2026-97689, msgpack GHSA-6v7p-g79w-8964, setuptools CVE-2025-47273). All four were inside pip's vendored libraries, not our application dependencies, so I removed pip from the runtime image. Both images now scan clean, which means no known fixable HIGH/CRITICAL vulnerabilities at scan time; it does not mean the images are vulnerability-free.

## M7 — Terraform (15)

| Criterion | Where |
|-----------|-------|
| Valid HCL | `terraform/*.tf` (`terraform validate` passes) |
| VPC with ≥ 2 public subnets | `module "vpc"`: 2 public + 2 private across 2 AZs |
| EKS + node group | `module "eks"`: managed node group `main` |
| `terraform.tfvars.example` | `terraform/terraform.tfvars.example` |

📸 `m7-plan.png`, `m7-aws-vpc.png`, `m7-aws-eks.png`, `m7-destroy.png`

## M8 — Kubernetes + Helm (15)

| Criterion | Where |
|-----------|-------|
| `k8s/namespace.yaml` | applies cleanly; enforces the restricted Pod Security Standard |
| Chart with Chart.yaml, values.yaml, templates | `helm/ironpulse/` |
| ≥ 2 replicas each | values: `backend.replicaCount: 2`, `frontend.replicaCount: 2`, HPA min 2 |
| ClusterIP Services | `templates/backend.yaml`, `templates/frontend.yaml` |
| Ingress `/` → frontend, `/api` → backend | `templates/ingress.yaml` |

📸 `m8-pods.png` (`kubectl get pods -n ironpulse`), `m8-svc.png`, `m8-helm-list.png`, `m8-ingress-browser.png`, `m8-hpa.png`

## M9 — Observability (10)

📸 `m9-metrics.png` (`curl http://<host>/api/../metrics`, or port-forward the backend and curl `/metrics`), `m9-prom-targets.png` (target `serviceMonitor/ironpulse/ironpulse-backend` UP), `m9-grafana.png` (IronPulse — API Overview dashboard with traffic: run `scripts/load-test.sh` first)

## M10 — Presentation (5)

`README.md` explains the app and every DevOps layer. Live demo script: `docs/DEMO.md`.

---

## Before you submit

- [ ] Repo is public (or instructor has access) and the URL is in the form
- [ ] Green Actions run on `main`
- [ ] GHCR packages show SHA tags (set package visibility to **public** so EKS can pull without a secret)
- [ ] All screenshots above captured
- [ ] `terraform destroy` completed and screenshot taken
- [ ] No secrets in history: `git log -p | grep -iE "aws_secret|password="` shows only placeholders
