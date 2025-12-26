#!/usr/bin/env bash

# ----------------------------------------------------------
# AI Observability Mega Demo – MIX mode – 2 hours
# ----------------------------------------------------------

DURATION_SECONDS=$((2 * 60 * 60))   # 2h
END_TIME=$(( $(date +%s) + DURATION_SECONDS ))
API_URL="http://localhost:8000/predict"

# Pondération du mix
# Chaque scénario a un poids → tirage proportionnel
SCENARIOS=(
  "baseline:50"
  "drift:15"
  "latency-spike:15"
  "high-risk:10"
  "toxic:5"
  "prompt-injection:3"
  "after-mitigation:2"
)

PROMPTS=(
  "Explain how observability reduces AI risks."
  "Analyse latency impact on quality."
  "What causes drift in real systems?"
  "Explain AI Act classification for this scenario."
  "Give me a summary of this text."
  "Describe a mitigation strategy."
)

pick_scenario() {
  local sum=0
  local rand=$((RANDOM % 100))

  for entry in "${SCENARIOS[@]}"; do
    IFS=":" read -r name weight <<< "$entry"
    sum=$((sum + weight))
    if (( rand < sum )); then
      echo "$name"
      return
    fi
  done
  echo "baseline"
}

echo "------------------------------------------------------"
echo "AI OBSERVABILITY – MIX MODE – 2h RUN"
echo "Start: $(date)"
echo "Expected end: $(date -r $END_TIME)"
echo "------------------------------------------------------"

COUNT=0

while [ "$(date +%s)" -lt "$END_TIME" ]; do

    SCENARIO=$(pick_scenario)
    PROMPT=${PROMPTS[$RANDOM % ${#PROMPTS[@]}]}

    # Variation : faible → moyenne → forte
    # LC_NUMERIC=C force l'utilisation du point comme séparateur décimal
    SLEEP=$(LC_NUMERIC=C awk -v min=0.05 -v max=0.45 \
        'BEGIN{srand(); v=min+rand()*(max-min); printf "%.3f\n", v}')

    curl -s -X POST "$API_URL" \
      -H "Content-Type: application/json" \
      -d "{\"prompt\": \"$PROMPT\", \"scenario\": \"$SCENARIO\"}" >/dev/null

    COUNT=$((COUNT+1))

    if (( COUNT % 50 == 0 )); then
      echo "[$(date '+%H:%M:%S')] Requests: $COUNT (current scenario: $SCENARIO)"
    fi

    sleep "$SLEEP"
done

echo "------------------------------------------------------"
echo "DEMO FINISHED – Total requests: $COUNT"
echo "------------------------------------------------------"

