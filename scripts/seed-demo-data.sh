#!/usr/bin/env bash
# Adds demo members and check-ins through the public API so dashboards have data.
# Usage: URL=http://localhost:3000 ./scripts/seed-demo-data.sh
set -euo pipefail
URL="${URL:-http://localhost:3000}"
API="$URL/api"

post() { curl -s -o /dev/null -w "%{http_code} $1\n" -X POST "$API/$1" -H 'Content-Type: application/json' -d "$2"; }

today=$(date +%F)
ago() { date -d "-$1 days" +%F 2>/dev/null || date -v-"$1"d +%F; }

post members "{\"full_name\":\"Ananya Gupta\",\"email\":\"ananya@example.com\",\"phone\":\"9876543210\",\"gender\":\"FEMALE\",\"plan_id\":2,\"trainer_id\":2,\"start_date\":\"$today\"}"
post members "{\"full_name\":\"Vikram Singh\",\"email\":\"vikram@example.com\",\"phone\":\"9876543211\",\"gender\":\"MALE\",\"plan_id\":1,\"trainer_id\":1,\"start_date\":\"$(ago 26)\"}"
post members "{\"full_name\":\"Karan Patel\",\"email\":\"karan@example.com\",\"phone\":\"9876543212\",\"gender\":\"MALE\",\"plan_id\":4,\"trainer_id\":3,\"start_date\":\"$(ago 60)\"}"
post members "{\"full_name\":\"Sneha Reddy\",\"email\":\"sneha@example.com\",\"phone\":\"9876543213\",\"gender\":\"FEMALE\",\"plan_id\":3,\"start_date\":\"$(ago 20)\"}"
post members "{\"full_name\":\"Rahul Verma\",\"email\":\"rahul@example.com\",\"phone\":\"9876543214\",\"gender\":\"MALE\",\"plan_id\":1,\"start_date\":\"$(ago 45)\"}"
post members "{\"full_name\":\"Meera Joshi\",\"email\":\"meera@example.com\",\"phone\":\"9876543215\",\"gender\":\"FEMALE\",\"plan_id\":4,\"trainer_id\":2,\"start_date\":\"$(ago 5)\"}"

for id in 1 2 3 4 6 1 3; do post checkins "{\"member_id\":$id}"; done
echo "Done. Open $URL"
