#!/usr/bin/env bash
# Generates CPU load on the backend so the HPA scales out. Watch it with:
#   kubectl get hpa -n ironpulse -w
#
# Usage: URL=http://<ingress-host> ./scripts/load-test.sh [duration_seconds] [parallel_workers]
set -euo pipefail

URL="${URL:-http://ironpulse.local}"
DURATION="${1:-180}"
WORKERS="${2:-20}"
# Dashboard stats + member listing touch the DB and serialise JSON: good CPU work.
ENDPOINTS=("/api/dashboard/stats" "/api/members" "/api/plans" "/api/checkins?limit=50")

echo "Hammering $URL with $WORKERS workers for ${DURATION}s..."
end=$((SECONDS + DURATION))
worker() {
  while (( SECONDS < end )); do
    for path in "${ENDPOINTS[@]}"; do
      curl -s -o /dev/null "$URL$path" || true
    done
  done
}
for _ in $(seq "$WORKERS"); do worker & done
wait
echo "Load test finished. Check: kubectl get hpa -n ironpulse"
