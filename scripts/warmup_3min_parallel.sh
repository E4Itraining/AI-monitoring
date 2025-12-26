# --- ajout automatique : fonction pick() compatible POSIX ---
pick() {
  set -- "$@"
  c=$#
  i=$((RANDOM % c + 1))
  eval "echo \${$i}"
}
# ------------------------------------------------------------

#!/usr/bin/env bash

# warmup_3min_parallel.sh
# Warm-up intensif parallèle (3 minutes)
# - N workers en parallèle
# - mélange baseline / drift léger / prompts un peu plus "limites"

BASE_URL="${BASE_URL:-http://localhost:8000}"
ENDPOINT="$BASE_URL/predict"

DURATION=${DURATION:-180}  # 3 minutes
WORKERS=${WORKERS:-8}

echo "=== Warm-up parallèle (3 min) ==="
echo "Endpoint : $ENDPOINT"
echo "Durée    : ${DURATION}s"
echo "Workers  : ${WORKERS}"
echo

call_api() {
  local payload="$1"
  curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    > /dev/null
}

worker_loop() {
  local wid="$1"
  local end=$((SECONDS + DURATION))

  while [ $SECONDS -lt $end ]; do
    MODE=$(pick baseline drift edge-case)

    case "$MODE" in
      baseline)
        PROMPT="Explique en quelques phrases un concept d'observabilité (worker $wid)."
        SCENARIO="baseline"
        ;;
      drift)
        PROMPT="Nouvelle gamme QX-$RANDOM avec contraintes exotiques et KPIs bizarres (drift soft, worker $wid)."
        SCENARIO="drift"
        ;;
      edge-case)
        PROMPT="Analyse ce log très long de production et propose un diagnostic détaillé (worker $wid)."
        SCENARIO="edge-case"
        ;;
    esac

    call_api "{\"prompt\": \"$PROMPT\", \"scenario\": \"$SCENARIO\"}"
    sleep 0.3
  done
}

for w in $(seq 1 "$WORKERS"); do
  worker_loop "$w" &
done

wait

echo "=== Warm-up parallèle terminé ==="
echo "→ Devrait alimenter : baseline + début de drift/edge-cases."

