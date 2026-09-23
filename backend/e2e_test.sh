#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:5001/api/v1/zk"

echo "=== 1. Generování ZK důkazu (/prove) ==="
PROVE_RESP=$(curl -s -X POST "$BASE_URL/prove" \
  -H "Content-Type: application/json" \
  -d '{"attribute": "age", "threshold": 18}')

TASK_ID_PROVE=$(echo "$PROVE_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo "Task ID (Prove): $TASK_ID_PROVE"

echo "Čekám na zpracování v Celery..."
sleep 1.5

PROVE_RESULT=$(curl -s "$BASE_URL/task/$TASK_ID_PROVE")
COMMITMENT=$(echo "$PROVE_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['commitment'])")
echo "Vygenerovaný commitment: $COMMITMENT"

echo -e "\n=== 2. Verifikace ZK důkazu (/verify) ==="
VERIFY_RESP=$(curl -s -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  -d "{\"attribute\": \"age\", \"threshold\": 18, \"commitment\": \"$COMMITMENT\"}")

TASK_ID_VERIFY=$(echo "$VERIFY_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo "Task ID (Verify): $TASK_ID_VERIFY"

echo "Čekám na zpracování v Celery..."
sleep 1.5

VERIFY_RESULT=$(curl -s "$BASE_URL/task/$TASK_ID_VERIFY")
VALID=$(echo "$VERIFY_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['valid'])")
echo "Výsledek verifikace: $VALID"

echo -e "\n=== 3. Vystavení eIDAS TSA razítka (/tsa) ==="
TSA_RESP=$(curl -s -X POST "$BASE_URL/tsa" \
  -H "Content-Type: application/json" \
  -d "{\"commitment\": \"$COMMITMENT\"}")

TASK_ID_TSA=$(echo "$TSA_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])")
echo "Task ID (TSA): $TASK_ID_TSA"

echo "Čekám na zpracování v Celery..."
sleep 1.5

TSA_RESULT=$(curl -s "$BASE_URL/task/$TASK_ID_TSA")
TSA_VALID=$(echo "$TSA_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['eidas_tsa_valid'])")
TSA_TOKEN=$(echo "$TSA_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['tsa_token'])")

echo "eIDAS TSA Platnost: $TSA_VALID"
echo "TSA Token: $TSA_TOKEN"

echo -e "\n✅ E2E ZK-Pipeline úspěšně dokončena!"
