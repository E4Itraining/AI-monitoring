# Grafana dashboard reading guide

1. Response quality
- Panel "AI Response Quality Score (avg)" shows the evolution of the quality score between 0 and 1.
- Target: stay above 0.7 in production.

2. Errors and hallucinations
- Panel "AI Errors & Hallucinations" shows error and suspected hallucination rates.
- Spikes when running scenarios B and C.

3. Latency
- Panel "AI Response Latency (p95)" shows the p95 latency.
- Use it to detect performance degradation under load.

4. Cost
- Panel "AI Estimated Cost (EUR)" shows estimated cost rate.
- Helps link performance, reliability and economic impact.
