# Test scenarios

Scenario A — Nominal
- Endpoint: POST /predict
- JSON body example: {"prompt": "Explain OSMC in one sentence", "scenario": "A"}

Scenario B — Data drift
- Endpoint: POST /predict
- JSON body example: {"prompt": "New product line QX-9000 with quantum-fused chips", "scenario": "B"}

Scenario C — Stress
- Run multiple POST /predict calls with scenario "C" in a loop to simulate load.
