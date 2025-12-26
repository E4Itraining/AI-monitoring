#!/usr/bin/env bash
# progressive_drift.sh
# Act II — Drift progressif : prompts de plus en plus éloignés du contexte "normal".

BASE_URL="${BASE_URL:-http://localhost:8000}"
ENDPOINT="$BASE_URL/predict"

DURATION=${DURATION:-180}  # 3 minutes
END=$((SECONDS + DURATION))
i=0

echo "=== Progressive DRIFT ==="
echo "Endpoint : $ENDPOINT"
echo "Durée    : ${DURATION}s"
echo

while [ $SECONDS -lt $END ]; do
  i=$((i+1))

  PROMPT="Scenario drift niveau $i : nouvelle gamme QX-9000-$i avec protocoles quantiques exotiques, contraintes inconnues et jargon non documenté."

  curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"scenario\": \"drift\"}" \
    > /dev/null &

  # dérive lente → ~1 requête toutes les 2s
  sleep 2
done

echo "=== Progressive DRIFT terminé ==="
echo "→ Vérifie 'Input topic drift' et 'Output quality score' avant/après."

