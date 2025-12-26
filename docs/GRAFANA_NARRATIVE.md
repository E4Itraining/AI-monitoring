# Grafana Narrative - AI Trustworthiness Observatory

> **Available in:** [English](GRAFANA_NARRATIVE.md) | [Français](GRAFANA_NARRATIVE_FR.md)

## Our Vision

Transform AI systems observability into a **strategic lever** that guarantees quality, security, compliance, and economic efficiency for your artificial intelligence deployments.

---

## What We Do

### A Complete Observability Platform for AI

We have built a **unified observatory** that monitors in real-time all critical aspects of an AI system in production:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI TRUSTWORTHINESS SUITE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   📊 QUALITY         🔒 SECURITY        📜 COMPLIANCE            │
│   ─────────          ─────────          ───────────              │
│   • Quality score    • Injection        • GDPR                   │
│   • Hallucinations   • Jailbreak        • AI Act                 │
│   • Coherence        • PII Detection    • Audit Trail            │
│                                                                  │
│   💰 COSTS           ⚡ PERFORMANCE      🌱 SUSTAINABILITY        │
│   ─────────          ───────────        ───────────              │
│   • Tokens           • Latency P99      • Tokens/request         │
│   • EUR/request      • Throughput       • Efficiency             │
│   • Anomalies        • SLO/SLI          • Optimization           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Architecture

Our stack relies on proven open-source technologies:

| Component | Role | Added Value |
|-----------|------|-------------|
| **Grafana 11** | Unified visualization | 4 dedicated business dashboards |
| **Prometheus/Victoria Metrics** | Metrics storage | 7x more RAM efficient |
| **Tempo** | Distributed traces | End-to-end correlation |
| **OpenSearch** | Structured logs | Full-text search |
| **AlertManager** | Intelligent alerting | 7 channels per team |

---

## What We Measure

### 50+ Metrics Organized in 6 Domains

#### 1. 📊 AI Response Quality

| Metric | Description | Target Threshold |
|--------|-------------|------------------|
| `ai_response_quality_score` | Global quality score (0-1) | > 0.80 |
| `ai_hallucination_events_total` | Hallucination detection | < 1% |
| `ai_coherence_score` | Contextual coherence | > 0.85 |
| `ai_user_satisfaction_score` | User satisfaction (1-5) | > 4.0 |

**Impact**: Ensure reliable and relevant responses that strengthen user trust.

#### 2. 🔒 Security & Protection

| Metric | Description | Action |
|--------|-------------|--------|
| `ai_prompt_injection_attempts_total` | Injection attempts | Automatic blocking |
| `ai_jailbreak_attempts_total` | Bypass attempts | Immediate alert |
| `ai_pii_detected_total` | Personal data detected | Masking/Blocking |
| `ai_toxicity_events_total` | Toxic content | Filtering |

**8 PII types detected**: email, phone, credit card, SSN, IBAN, IP, date of birth, name.

#### 3. 📜 Regulatory Compliance

| Metric | Description | Regulation |
|--------|-------------|------------|
| `ai_gdpr_compliance_score` | GDPR compliance score | GDPR |
| `ai_compliance_score{category="ai_act"}` | AI Act score | AI Act |
| `ai_trust_index` | Global trust index | Multi-framework |
| `ai_risk_level_gauge` | Risk level (low→critical) | AI Act Article 6 |

#### 4. 💰 Economics & Costs

| Metric | Description | Optimization |
|--------|-------------|--------------|
| `ai_tokens_input_total` | Input tokens consumed | Per model |
| `ai_tokens_output_total` | Output tokens generated | Per model |
| `ai_cost_estimated_eur_total` | Cumulative cost in EUR | Real-time |
| Cost/request | EUR per request | Anomaly alerts |

#### 5. ⚡ Performance & SLO

| Metric | Description | SLO |
|--------|-------------|-----|
| `ai_latency_seconds` (P99) | 99th percentile latency | < 1000ms |
| `ai_requests_error_total` | Error rate | < 0.5% |
| `ai_slo_compliance_ratio` | Overall SLO compliance | > 99.5% |
| `ai_error_budget_burn_rate` | Error budget burn velocity | < 1.0 |

#### 6. 🔄 Semantic Drift

| Metric | Description | Dimension |
|--------|-------------|-----------|
| `ai_input_drift_score{dimension="topic"}` | Topic drift | Subject |
| `ai_input_drift_score{dimension="domain"}` | Domain drift | Expertise |
| `ai_input_drift_score{dimension="complexity"}` | Complexity drift | Difficulty |
| `ai_out_of_domain_total` | Out-of-domain prompts | Scope |

---

## The Impact

### Technical Impact

| Before | After | Gain |
|--------|-------|------|
| Undetected incidents | Proactive detection < 5min | **-80% MTTR** |
| Blind debugging | E2E correlated traces | **-60% debug time** |
| Manual metrics | Complete automation | **100% coverage** |
| Noisy alerts | Intelligent routed alerting | **-70% false positives** |

### Business Impact

| Dimension | Benefit | Measure |
|-----------|---------|---------|
| **Customer trust** | Verified AI responses | Trust Index > 0.85 |
| **Cost reduction** | Token optimization | -15-30% LLM invoice |
| **Time-to-market** | Confident deployment | +50% release velocity |
| **Legal risk** | Provable compliance | Complete audit trail |

### Compliance Impact

| Regulation | Requirement | Coverage |
|------------|-------------|----------|
| **GDPR** | Personal data protection | PII Detection + Masking |
| **AI Act** | Risk management | Classification + Monitoring |
| **AI Act** | Transparency | Audit trail + Traceability |
| **AI Act** | Documentation | Dashboards + Export |

### Environmental Impact (GreenOps)

| Metric | Optimization | Impact |
|--------|--------------|--------|
| Tokens/request | Verbose prompt reduction | -20% consumption |
| Unnecessary requests | Intelligent caching | -30% API calls |
| Adapted model | Model right-sizing | -40% compute |

---

## Persona Journeys

### 🔧 TECH Persona (SRE / DevOps / ML Engineer)

**Objective**: Maintain reliability and performance of the AI system in production.

#### Main Dashboard: `AI Reliability Overview`

```
┌─────────────────────────────────────────────────────────────────┐
│                    🔧 SRE / TECH VIEW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Quality: 0.87│  │ Latency P99  │  │ Error Rate   │           │
│  │    ████████  │  │   234ms      │  │    0.2%      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LATENCY DISTRIBUTION (24h)                  │    │
│  │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  🔔 Active alerts: 0 Critical | 1 Warning                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Daily Workflow

1. **Morning Check** (5 min)
   - Check SLO dashboard: Error budget consumed?
   - Scan overnight alerts
   - Review P99 latency trend

2. **Incident Response**
   - Click on alert → Drill-down to Tempo traces
   - Correlate with OpenSearch logs
   - Identify problematic scenario (drift, load, injection)

3. **Capacity Planning**
   - Analyze `ai_inflight_requests` to anticipate scaling
   - Monitor `ai_rate_limit_events_total` to adjust limits

#### Configured Alerts

| Alert | Threshold | Action |
|-------|-----------|--------|
| `HighLatencyP99` | > 1000ms for 5min | Performance investigation |
| `ErrorBudgetBurnRateHigh` | > 2x normal | Deployment review |
| `ServiceDown` | 0 requests for 2min | Major incident |

---

### 💼 BUSINESS Persona (Product Owner / Manager)

**Objective**: Understand the business value and risks of deployed AI.

#### Main Dashboard: `AI Trustworthiness Suite v4.0`

```
┌─────────────────────────────────────────────────────────────────┐
│                    💼 BUSINESS VIEW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    TRUST INDEX                            │   │
│  │                                                           │   │
│  │              ████████████████░░░░  0.87 / 1.0            │   │
│  │                                                           │   │
│  │   ✅ Quality: OK    ✅ Security: OK    ⚠️ Costs: High    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Satisfaction│  │ Daily Cost  │  │ Conversations│             │
│  │    ⭐ 4.2   │  │   €47.50    │  │     1,234    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  📈 Satisfaction trend: +5% vs last week                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Key KPIs

| KPI | Description | Target |
|-----|-------------|--------|
| **Trust Index** | Global trust index | > 0.85 |
| **User Satisfaction** | Average user rating | > 4.0/5 |
| **Cost/Conversation** | Average cost per exchange | < €0.05 |
| **Hallucination Rate** | % of questionable responses | < 1% |

#### Questions the Dashboard Answers

- *"Is the AI responding correctly?"* → Quality Score + Satisfaction
- *"How much does it cost?"* → Cost panels + Trend
- *"Is it risky?"* → Risk Level + Security Score
- *"Are users satisfied?"* → Feedback Score

#### Auto-generated Weekly Report

```
📊 WEEKLY AI REPORT - Week 42

✅ Average Trust Index: 0.87 (+2%)
✅ User satisfaction: 4.2/5 (+0.1)
✅ Availability: 99.8%
⚠️ Total cost: €347 (+15% vs budget)
✅ Security incidents: 0 critical
```

---

### 📜 COMPLIANCE Persona (DPO / Legal / Risk Manager)

**Objective**: Ensure regulatory compliance and document AI governance.

#### Main Dashboard: Dedicated panels in `AI Trustworthiness Suite`

```
┌─────────────────────────────────────────────────────────────────┐
│                    📜 COMPLIANCE VIEW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐             │
│  │    GDPR SCORE        │  │    AI ACT RISK       │             │
│  │                      │  │                      │             │
│  │   ████████████ 0.92  │  │   🟢 LOW RISK        │             │
│  │                      │  │   Classification: OK │             │
│  └──────────────────────┘  └──────────────────────┘             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              PII DETECTION (last 7 days)                 │    │
│  │                                                          │    │
│  │  Email: 45 detected | 45 masked | 0 leaked              │    │
│  │  Phone: 12 detected | 12 masked | 0 leaked              │    │
│  │  IBAN:  3 detected  |  3 blocked | 0 leaked             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  📋 Audit events this week: 12,456 (100% traced)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Regulatory Requirements Covered

##### GDPR (General Data Protection Regulation)

| Article | Requirement | Coverage |
|---------|-------------|----------|
| Art. 5 | Data minimization | PII Detection + Masking |
| Art. 17 | Right to erasure | Conversation deletion API |
| Art. 30 | Records of processing | Complete audit trail |
| Art. 33 | Breach notification | Real-time alerts |

##### AI Act (European AI Regulation)

| Article | Requirement | Coverage |
|---------|-------------|----------|
| Art. 9 | Risk management | `ai_risk_level_gauge` |
| Art. 12 | Record-keeping | OpenSearch logs + Trace IDs |
| Art. 13 | Transparency | Accessible dashboards |
| Art. 14 | Human oversight | Configurable guardrails |

#### Compliance Alerts

| Alert | Trigger | Escalation |
|-------|---------|------------|
| `GDPRComplianceLow` | Score < 0.8 | compliance@example.com |
| `AIActHighRisk` | Critical level | DPO + Legal |
| `HighPIIDetectionRate` | > 0.5/sec | Immediate investigation |

#### Audit Export

```bash
# Export audit events for inspection
curl "http://opensearch:9200/ai-logs/_search?q=event_type:audit" \
  -H "Content-Type: application/json" > audit_export.json
```

---

### 🌱 GREENOPS Persona (Sustainability / FinOps / Efficiency)

**Objective**: Optimize the environmental and economic footprint of AI.

#### Dashboard Focus: Cost & Efficiency Panels

```
┌─────────────────────────────────────────────────────────────────┐
│                    🌱 GREENOPS VIEW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              TOKEN EFFICIENCY TREND                       │    │
│  │                                                           │    │
│  │  Input Tokens/req:  ▼ 1,245 (-8% vs baseline)            │    │
│  │  Output Tokens/req: ▼ 856 (-12% vs baseline)             │    │
│  │  Cost/req:          ▼ €0.032 (-15% vs baseline)          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Daily Cost   │  │ Waste Ratio  │  │ Cache Hit    │           │
│  │   €47.50     │  │    12%       │  │    34%       │           │
│  │   ▼ vs yday  │  │   ⚠️ high    │  │   ✅ good    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  🌍 CO2 Estimate: ~2.3 kg/day (based on cloud usage)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Efficiency Metrics

| Metric | Formula | Objective |
|--------|---------|-----------|
| **Token Efficiency** | Useful tokens / Total tokens | > 85% |
| **Cost per Value** | Cost / Satisfaction | Minimize |
| **Waste Ratio** | Failed requests / Total | < 5% |
| **Model Right-sizing** | Quality / Model cost | Optimize |

#### Identifiable Optimization Strategies

1. **Prompt Engineering**
   - Monitor `ai_tokens_input_total` by scenario
   - Identify verbose prompts (> 2000 tokens)
   - Target: -20% input tokens

2. **Intelligent Caching**
   - Analyze similar request patterns
   - Implement semantic caching
   - Target: -30% API calls

3. **Model Selection**
   - Compare quality/cost by model via labels
   - Route simple requests to lighter models
   - Target: -40% cost without quality loss

4. **Proactive Rate Limiting**
   - Monitor `ai_rate_limit_events_total`
   - Avoid consumption spikes
   - Smooth the load

#### Recommended FinOps Dashboard

```
Rate(ai_cost_estimated_eur_total[1h]) * 24 * 30  → Monthly projection
Rate(ai_tokens_input_total[1d]) / count(ai_requests_total[1d]) → Tokens/req
```

---

## Dashboard Summary by Persona

| Persona | Main Dashboard | Frequency | Key Metrics |
|---------|----------------|-----------|-------------|
| **🔧 Tech** | AI Reliability + SLO | Continuous | Latency, Errors, SLO |
| **💼 Business** | AI Trustworthiness Suite | Daily | Trust Index, Satisfaction, Cost |
| **📜 Compliance** | Compliance Panels | Weekly/Audit | GDPR Score, PII, Risk Level |
| **🌱 GreenOps** | Cost Panels + Custom | Monthly | Tokens, EUR/req, Efficiency |

---

## Getting Started

### Quick Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |

### First Steps by Persona

1. **Tech**: Open `AI Reliability Overview` → Check SLO compliance
2. **Business**: Open `AI Trustworthiness Suite` → Read Trust Index
3. **Compliance**: Filter GDPR panels → Export audit logs
4. **GreenOps**: Create custom dashboard with cost metrics

---

## Conclusion

This AI observability platform transforms raw monitoring data into **actionable insights** for every stakeholder. By unifying quality, security, compliance, and efficiency in a single observatory, we enable each persona to make informed decisions based on reliable, real-time data.

> *"What gets measured gets improved."* - Peter Drucker

With our AI Trustworthiness Observatory, every aspect of your AI in production is not only measured but optimizable.
