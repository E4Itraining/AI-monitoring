#!/usr/bin/env bash
# latence_stress.sh
# Act II — Stress de latence : bursts rapides pour faire monter p95, files d'attente, éventuels rate-limits.

BASE_URL="${BASE_URL:-http://localhost:8000}"
ENDPOINT="$BASE_URL/predict"

DURATION=${DURATION:-180}  # 3 minutes
BURST_SIZE=${BURST_SIZE:-20}
PAUSE=${PAUSE:-3}

echo "=== Latency STRESS ==="
echo "Endpoint : $ENDPOINT"
echo "Durée    : ${DURATION}s"
echo "Burst    : ${BURST_SIZE} requêtes toutes les ${PAUSE}s"
echo

END=$((SECONDS + DURATION))

while [ $SECONDS -lt $END ]; do
  echo "[LATENCY] Nouveau burst..."
  for i in $(seq 1 "$BURST_SIZE"); do
    PROMPT="Requête de stress latence $i sur scénario latency-spike."
    curl -s -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -d "{\"prompt\": \"$PROMPT\", \"scenario\": \"latency-spike\"}" \
      > /dev/null &
  done

  sleep "$PAUSE"
done

echo "=== Latency STRESS terminé ==="
echo "→ Vérifie les panels 'Load Spikes & Latency' (RPS, p95, queue, rate limits)."

