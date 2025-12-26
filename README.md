# AI-Monitoring Platform

## Plateforme d'Observabilité pour Applications IA

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/E4Itraining/AI-monitoring)
[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Plateforme complète de monitoring et d'observabilité pour applications IA, avec conformité RGPD/AI Act, détection de dérive sémantique, analyse de sécurité et gestion des SLO.

---

## Table des Matières

- [Présentation](#présentation)
- [Fonctionnalités Clés](#fonctionnalités-clés)
- [Architecture](#architecture)
- [Stack Technique](#stack-technique)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Dashboards Grafana](#dashboards-grafana)
- [Alerting](#alerting)
- [Documentation](#documentation)

---

## Présentation

**AI-Monitoring** est une solution d'observabilité avancée conçue pour monitorer et sécuriser les applications IA en production. La plateforme offre trois architectures de déploiement adaptées à différents besoins :

| Architecture | Cas d'usage | Services |
|-------------|-------------|----------|
| **Standard** | Développement, POC | 8 containers |
| **Enhanced** | Pré-production | 9 containers + health checks |
| **Scalable** | Production | 11 containers haute performance |

---

## Fonctionnalités Clés

### Sécurité & Conformité
- **Détection PII** : Email, téléphone, CB, SSN, IBAN, IP (conformité RGPD)
- **Analyse Prompt** : Détection injection, jailbreak, manipulation de rôle
- **Guardrails** : Règles configurables (toxicité, longueur, rate limiting)
- **Niveau de risque AI Act** : Classification automatique

### Observabilité IA
- **Drift Detection** : Détection de dérive sémantique en temps réel
- **Quality Score** : Score de qualité des réponses (0-1)
- **Trust Index** : Index de confiance composite
- **Hallucination Tracking** : Suivi des hallucinations

### Opérationnel
- **SLO/SLI** : Suivi latence P99 < 1s, qualité > 0.8
- **Error Budget** : Calcul automatique du burn rate
- **Cost Tracking** : Estimation des coûts en EUR
- **Audit Trail** : Traçabilité complète avec UUID

---

## Architecture

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI Application (FastAPI)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ PII Detect  │  │  Security   │  │    Drift    │  │   Guardrails    │ │
│  │   Service   │  │  Analyzer   │  │  Detector   │  │     System      │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘ │
│         └────────────────┴────────────────┴──────────────────┘          │
│                                    │                                     │
│         ┌──────────────────────────┼──────────────────────────┐         │
│         │                          │                          │         │
│    /metrics                   OTLP Export                 JSON Logs     │
└─────────┼──────────────────────────┼──────────────────────────┼─────────┘
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Prometheus    │    │   OTel Collector     │    │     Fluent-bit      │
│   / Victoria    │    │   (Gateway)          │    │   (Log Shipper)     │
│    Metrics      │    │                      │    │                     │
└────────┬────────┘    └──────────┬───────────┘    └──────────┬──────────┘
         │                        │                           │
         │           ┌────────────┼────────────┐              │
         │           │            │            │              │
         │           ▼            ▼            ▼              ▼
         │    ┌───────────┐ ┌──────────┐ ┌───────────┐ ┌────────────┐
         │    │   Tempo   │ │OpenObserve│ │ OpenSearch│ │ OpenSearch │
         │    │ (Traces)  │ │(Unified) │ │  (Logs)   │ │ Dashboards │
         │    └─────┬─────┘ └────┬─────┘ └─────┬─────┘ └────────────┘
         │          │            │             │
         └──────────┴────────────┴─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │     Grafana      │
                    │  (Dashboards)    │
                    │                  │
                    │ - Trustworthiness│
                    │ - Reliability    │
                    │ - SLO Dashboard  │
                    │ - Observability  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   AlertManager   │
                    │  (Routing)       │
                    │                  │
                    │ - Security Team  │
                    │ - SRE Team       │
                    │ - ML Team        │
                    └──────────────────┘
```

### Flux de Données

#### 1. Métriques
```
App → /metrics → Prometheus/Victoria Metrics → Grafana
                       ↓
              Alert Rules → AlertManager → Notifications
```

#### 2. Traces
```
App → OTLP → OTel Collector → Tempo → Grafana (Trace View)
                  ↓
           Tail Sampling (erreurs, lent, 10% sample)
```

#### 3. Logs
```
App → /logs/app.log → Fluent-bit → OpenSearch → Grafana
                          ↓
                      OpenObserve (backup)
```

---

## Stack Technique

### Composants Principaux

| Composant | Version | Port | Rôle |
|-----------|---------|------|------|
| **FastAPI** | Python 3.11 | 8000 | Application IA |
| **Prometheus** | 2.51.1 | 9090 | Collecte métriques |
| **Victoria Metrics** | 1.96.0 | 8428 | Stockage scalable (7x RAM efficiency) |
| **Grafana** | 11.0.0 | 3000 | Visualisation |
| **Tempo** | 2.6.0 | 3200 | Tracing distribué |
| **OpenTelemetry** | 0.94.0 | 4317/4318 | Gateway telemetrie |
| **OpenSearch** | 2.13.0 | 9200 | Logs full-text |
| **Fluent-bit** | 2.2.3 | 2020 | Collection logs |
| **AlertManager** | 0.27.0 | 9093 | Routage alertes |
| **OpenObserve** | 0.10.0 | 5080 | Plateforme unifiée |

### Métriques Exportées (50+)

```python
# Trafic
ai_requests_total{scenario, status}
ai_inflight_requests

# Qualité
ai_response_quality_score
ai_hallucination_events_total
ai_coherence_score

# Sécurité
ai_prompt_security_score
ai_pii_detected_total{type}
ai_jailbreak_attempts_total
ai_prompt_injection_attempts_total

# Drift
ai_input_drift_score
ai_drift_alerts_total{severity}

# Coût
ai_cost_estimated_eur_total
ai_tokens_input_total
ai_tokens_output_total

# Guardrails
ai_guardrail_triggers_total{guardrail}
ai_guardrail_blocked_total{guardrail}

# Trust & Compliance
ai_trust_index
ai_compliance_score
ai_risky_responses_total{risk_level}

# SLO
ai_sli_latency_success_total
ai_sli_latency_violations_total
ai_sli_quality_success_total
ai_slo_error_budget_burn_rate
```

---

## Installation

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 4 GB RAM minimum (8 GB recommandé pour stack scalable)

### Déploiement Rapide

```bash
# Cloner le repository
git clone https://github.com/E4Itraining/AI-monitoring.git
cd AI-monitoring

# Copier la configuration
cp .env.example .env

# Démarrer la stack standard
docker-compose up -d --build

# OU stack enhanced (avec alerting)
docker-compose -f docker-compose-enhanced.yml up -d --build

# OU stack scalable (production)
docker-compose -f docker-compose.scalable.yml up -d --build
```

### Vérification

```bash
# Vérifier les services
docker ps

# Tester l'application
curl http://localhost:8000/health

# Tester une prédiction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explique le monitoring IA", "scenario": "A"}'
```

### Accès aux Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **OpenSearch Dashboards** | http://localhost:5601 | admin / admin |
| **Tempo** | http://localhost:3200 | - |
| **AlertManager** | http://localhost:9093 | - |
| **OpenObserve** | http://localhost:5080 | admin@ai-monitoring.local / ComplexPass123! |

---

## Configuration

### Variables d'Environnement

```bash
# Service Versions
PROMETHEUS_VERSION=2.51.1
GRAFANA_VERSION=11.0.0
TEMPO_VERSION=2.6.0
VICTORIA_METRICS_VERSION=1.96.0

# Credentials (CHANGER EN PRODUCTION)
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin

# OpenTelemetry
OTEL_SERVICE_NAME=ai-lab-app
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# SLO Configuration
SLO_LATENCY_THRESHOLD_MS=1000
SLO_QUALITY_THRESHOLD=0.8
```

### Configuration des Guardrails

```bash
# Activer/configurer un guardrail
curl -X PUT http://localhost:8000/guardrails/config \
  -H "Content-Type: application/json" \
  -d '{
    "guardrail_name": "pii_protection",
    "enabled": true,
    "threshold": 0
  }'

# Guardrails disponibles
# - pii_protection: Bloque si PII détecté
# - injection_protection: Bloque si injection > seuil
# - toxicity_filter: Filtre contenu toxique
# - rate_limiter: Limite 100 req/min/client
# - prompt_length: Limite longueur prompt
```

---

## Utilisation

### API Endpoints

```bash
# Info service
GET /

# Health check
GET /health

# Métriques Prometheus
GET /metrics

# Prédiction principale
POST /predict
{
  "prompt": "string",
  "scenario": "A" | "B" | "C",
  "user_id": "optional",
  "conversation_id": "optional"
}

# Feedback utilisateur
POST /feedback
{
  "request_id": "uuid",
  "rating": 1-5,
  "comment": "optional",
  "category": "optional"
}

# Gestion conversations
GET /conversations/{conversation_id}
DELETE /conversations/{conversation_id}

# Statistiques
GET /stats

# Guardrails
GET /guardrails
PUT /guardrails/config
```

### Scénarios de Test

| Scénario | Description | Comportement |
|----------|-------------|--------------|
| **A** | Baseline | Qualité > 0.8, latence < 100ms |
| **B** | Data Drift | Dérive sémantique, qualité variable |
| **C** | Stress | Latence dégradée, rate limiting |

```bash
# Test de charge
python ai_load_client.py --scenario A --requests 100 --concurrency 10
```

---

## Dashboards Grafana

### 1. AI Trustworthiness Suite
Surveillance complète de la qualité et sécurité IA :
- Score de qualité des réponses
- Détection hallucinations
- Score de sécurité
- Détection PII
- Index de confiance

### 2. AI Reliability Overview
Focus SRE et fiabilité :
- Latence P95/P99
- Taux d'erreur
- Disponibilité
- Métriques RED

### 3. SLO Dashboard
Suivi des objectifs de niveau de service :
- Latence P99 < 1000ms
- Qualité > 0.8
- Error budget burn rate
- Violations SLI

### 4. Observability Dashboard
Santé de l'infrastructure :
- État des services
- Métriques système
- Logs en temps réel
- Traces

---

## Alerting

### Catégories d'Alertes

| Catégorie | Récepteur | Exemples |
|-----------|-----------|----------|
| **Quality** | ML Team | Score < 0.6, hallucinations |
| **Security** | Security Team | Injection, jailbreak, PII |
| **Compliance** | Compliance Team | Violations RGPD |
| **SLO** | SRE Team | Error budget burn |
| **Infrastructure** | Ops Team | Services down |
| **Cost** | Cost Team | Anomalies coût |

### Alertes Principales

```yaml
AIQualityScoreLow:
  condition: avg(ai_response_quality_score) < 0.6 for 5m
  severity: warning

AIQualityScoreCritical:
  condition: avg(ai_response_quality_score) < 0.4 for 2m
  severity: critical

PromptInjectionDetected:
  condition: rate(ai_prompt_injection_attempts_total) > 5 in 5m
  severity: critical

JailbreakAttemptDetected:
  condition: rate(ai_jailbreak_attempts_total) > 3 in 5m
  severity: critical

SemanticDriftHigh:
  condition: ai_input_drift_score > 0.7 for 5m
  severity: warning

ErrorBudgetBurnRateHigh:
  condition: ai_slo_error_budget_burn_rate > 2
  severity: warning
```

---

## Documentation

Documentation détaillée dans le dossier `/docs` :

| Document | Description |
|----------|-------------|
| [01-setup.md](docs/01-setup.md) | Guide d'installation |
| [02-scenarios.md](docs/02-scenarios.md) | Scénarios de test |
| [03-grafana-reading-guide.md](docs/03-grafana-reading-guide.md) | Guide dashboards |
| [architecture-scalable-analysis.md](docs/architecture-scalable-analysis.md) | Analyse architecture scalable |
| [migration-scalable.md](docs/migration-scalable.md) | Guide de migration |
| [runbook.md](docs/runbook.md) | Procédures opérationnelles |

---

## Structure du Projet

```
AI-monitoring/
├── app/                          # Application FastAPI
│   ├── main.py                   # Application principale (1500+ lignes)
│   ├── requirements.txt          # Dépendances Python
│   └── Dockerfile                # Image Docker
│
├── docker-compose.yml            # Stack standard
├── docker-compose-enhanced.yml   # Stack avec alerting
├── docker-compose.scalable.yml   # Stack production
│
├── prometheus/                   # Configuration Prometheus
│   ├── prometheus.yml            # Scrape config
│   ├── prometheus-enhanced.yml   # Version enhanced
│   └── alert-rules.yml           # Règles d'alertes
│
├── grafana/                      # Configuration Grafana
│   ├── provisioning/             # Auto-provisioning
│   │   ├── datasources/          # Sources de données
│   │   └── dashboards/           # Config dashboards
│   └── dashboards/               # Fichiers JSON dashboards
│
├── otel-collector-config/        # OpenTelemetry Collector
│   ├── config.yaml               # Config basique
│   └── config-scalable.yaml      # Config avancée
│
├── tempo/                        # Tempo (tracing)
│   ├── tempo.yml                 # Config basique
│   └── tempo-scalable.yml        # Config scalable
│
├── fluent-bit/                   # Fluent-bit (logs)
│   ├── fluent-bit.conf           # Config basique
│   ├── fluent-bit-scalable.conf  # Dual output
│   └── parsers.conf              # Parsers
│
├── alertmanager/                 # AlertManager
│   └── alertmanager.yml          # Routing des alertes
│
├── victoria-metrics/             # Victoria Metrics
│   └── scrape.yml                # Scrape config
│
├── opensearch/                   # OpenSearch data
├── docs/                         # Documentation
├── scripts/                      # Scripts utilitaires
├── logs/                         # Logs application
└── .env.example                  # Template configuration
```

---

## Performance (Stack Scalable)

| Métrique | Standard | Scalable | Amélioration |
|----------|----------|----------|--------------|
| RAM métriques | 2 GB | 300 MB | **7x** |
| Latence requête | 500ms | 50ms | **10x** |
| Stockage 30j | 50 GB | 15 GB | **3x** |
| Temps démarrage | 45s | 20s | **2x** |

---

## Contribuer

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

---

## Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

## Support

- **Issues** : [GitHub Issues](https://github.com/E4Itraining/AI-monitoring/issues)
- **Documentation** : Dossier `/docs`
- **Runbook** : [docs/runbook.md](docs/runbook.md)

---

**Version 4.0.0** | Dernière mise à jour : Décembre 2025
