# Analyse Architecture Scalable - AI Monitoring Platform

## Executive Summary

Ce document analyse l'architecture actuelle et propose une réorientation vers des solutions plus scalables et modernes pour l'observabilité AI.

---

## 1. Architecture Actuelle - Analyse des Limites

### Stack Actuelle

| Composant | Solution | Version | Limites de Scalabilité |
|-----------|----------|---------|------------------------|
| **Métriques** | Prometheus | 2.51.1 | Single node, pas de clustering natif |
| **Visualisation** | Grafana | 11.0.0 | OK - conservé |
| **Traces** | Tempo | 2.6.0 | Storage local uniquement |
| **Logs** | OpenSearch | 2.13.0 | Lourd en ressources, complexe |
| **Collecte** | OpenTelemetry | 0.94.0 | OK - renforcé |
| **Log Shipper** | Fluent-bit | 2.2.3 | OK - léger et efficace |

### Problèmes Identifiés

#### 1. Prometheus - Goulot d'Étranglement
```
⚠️ Single node architecture
⚠️ Pas de réplication native
⚠️ Rétention limitée par le storage local
⚠️ Pas de haute disponibilité sans solutions tierces (Thanos, Cortex)
⚠️ Consommation mémoire élevée avec beaucoup de séries temporelles
```

#### 2. Tempo - Storage Non Distribué
```
⚠️ Configuration actuelle: storage local /var/tempo/traces
⚠️ Pas de réplication des traces
⚠️ Point de défaillance unique
⚠️ Rétention limitée (24-48h actuellement)
```

#### 3. OpenSearch - Surcharge Opérationnelle
```
⚠️ Consommation mémoire importante (heap JVM)
⚠️ Configuration sécurité complexe
⚠️ Overhead pour de simples logs AI
```

---

## 2. Solutions Scalables Proposées

### 2.1 Victoria Metrics (Remplacement Prometheus)

**Pourquoi Victoria Metrics ?**

| Critère | Prometheus | Victoria Metrics |
|---------|------------|------------------|
| **Clustering** | Non natif | Oui, natif |
| **Compression** | ~1.5 bytes/point | ~0.7 bytes/point (2x meilleur) |
| **Performance queries** | Bonne | 10-20x plus rapide |
| **Compatibilité PromQL** | 100% | 100% + extensions |
| **Haute disponibilité** | Via Thanos/Cortex | Natif (vmcluster) |
| **Ressources** | Élevées | 7x moins de RAM |
| **Remote write** | Support limité | Optimisé |

**Modes de déploiement :**

```
┌─────────────────────────────────────────────────────────────┐
│  Single Node (développement/petite prod)                    │
│  victoria-metrics:latest                                    │
│  - Tout-en-un, simple                                       │
│  - Jusqu'à 10M metrics/sec                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Cluster Mode (production scalable)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐        │
│  │ vminsert    │  │ vmstorage    │  │ vmselect    │        │
│  │ (ingestion) │  │ (stockage)   │  │ (queries)   │        │
│  │ HA: N nodes │  │ HA: N shards │  │ HA: N nodes │        │
│  └─────────────┘  └──────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 OpenObserve (Alternative Unifiée)

**Pourquoi OpenObserve ?**

OpenObserve est une plateforme unifiée pour logs, métriques et traces - potentiellement le remplacement de toute la stack actuelle.

| Critère | Stack Actuelle | OpenObserve |
|---------|----------------|-------------|
| **Composants** | 5+ services | 1 service |
| **Storage** | 100% | ~10% (compression Zstd) |
| **Setup** | Complexe | Simple |
| **Query Language** | PromQL + SQL + Lucene | SQL unifié |
| **S3 Compatible** | Configuration manuelle | Natif |
| **Coût opérationnel** | Élevé | Faible |

**Architecture OpenObserve :**

```
┌───────────────────────────────────────────────────────────────┐
│                      OpenObserve                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Ingestion Layer                       │  │
│  │  OTLP │ Prometheus │ Fluent-bit │ HTTP/JSON             │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Storage Layer                         │  │
│  │  Logs │ Metrics │ Traces (Parquet + Zstd compression)   │  │
│  │  Local disk ou S3/MinIO/GCS                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Query Layer                           │  │
│  │  SQL │ PromQL Compatible │ Full-text search             │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    UI Dashboard                          │  │
│  │  Built-in visualization (alternative à Grafana)         │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 2.3 OpenTelemetry (Renforcement)

L'OpenTelemetry Collector est déjà en place. Renforcement proposé :

```yaml
# Configuration enrichie pour multi-backend
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
        - job_name: 'ai-app'
          static_configs:
            - targets: ['app:8000']

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  resourcedetection:
    detectors: [env, docker]
  attributes:
    actions:
      - key: environment
        value: production
        action: upsert

exporters:
  # Métriques vers Victoria Metrics
  prometheusremotewrite:
    endpoint: http://victoria-metrics:8428/api/v1/write

  # Traces vers Tempo ou OpenObserve
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Logs vers OpenObserve
  otlphttp/openobserve:
    endpoint: http://openobserve:5080/api/default
    headers:
      Authorization: "Basic ${OPENOBSERVE_TOKEN}"

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resourcedetection]
      exporters: [otlp/tempo]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [otlphttp/openobserve]
```

### 2.4 OpenSearch (Optimisation)

OpenSearch reste pertinent pour les logs avec recherche full-text complexe. Optimisations :

```yaml
# Index Lifecycle Management pour AI logs
PUT _ilm/policy/ai-logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "10gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

---

## 3. Architectures Proposées

### Option A : Stack Hybride (Recommandée pour Production)

Remplace Prometheus par Victoria Metrics, conserve Tempo et OpenSearch optimisés.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Application                               │
│    (FastAPI + OpenTelemetry SDK + Prometheus Client Library)        │
└────────────┬──────────────────────────────────────────┬─────────────┘
             │ OTLP (traces, metrics, logs)             │ JSON logs
             ▼                                          ▼
┌────────────────────────┐                 ┌──────────────────────┐
│  OpenTelemetry         │                 │  Fluent-bit          │
│  Collector (Gateway)   │                 │  (Log collection)    │
│  - Enrichment          │                 └──────────┬───────────┘
│  - Sampling            │                            │
│  - Multi-export        │                            │
└────┬──────┬───────┬────┘                            │
     │      │       │                                 │
     ▼      ▼       ▼                                 ▼
┌────────┐ ┌─────┐ ┌────────────────┐    ┌──────────────────────┐
│Victoria│ │Tempo│ │ OpenObserve    │    │ OpenSearch           │
│Metrics │ │     │ │ (Logs unified) │ OR │ (Full-text search)   │
│        │ │     │ │                │    │                      │
└────┬───┘ └──┬──┘ └───────┬────────┘    └──────────┬───────────┘
     │        │            │                        │
     └────────┴─────┬──────┴────────────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │     Grafana     │
           │  - VictoriaM DS │
           │  - Tempo DS     │
           │  - OpenSearch DS│
           └─────────────────┘
```

**Avantages :**
- Migration progressive possible
- Victoria Metrics apporte 7x moins de RAM, meilleure performance
- Tempo conservé (traces déjà configurées)
- Choix entre OpenObserve (simple) ou OpenSearch (full-text avancé)

### Option B : Stack Unifiée OpenObserve

Remplace TOUTE la stack par OpenObserve (sauf Grafana optionnel).

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Application                               │
│    (FastAPI + OpenTelemetry SDK)                                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ OTLP (all signals)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenTelemetry Collector                          │
│              (Gateway avec processing unifié)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │ OTLP HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenObserve                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Unified Storage: Logs + Metrics + Traces                     │   │
│  │ - Compression Zstd (10x moins de storage)                    │   │
│  │ - S3/MinIO backend pour scalabilité                          │   │
│  │ - Query SQL + PromQL                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Built-in Dashboards + Alerting                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │ (optionnel)
         ▼
┌─────────────────────┐
│  Grafana            │
│  (si dashboards     │
│   existants requis) │
└─────────────────────┘
```

**Avantages :**
- Complexité opérationnelle minimale (1 service vs 5+)
- Coût storage réduit de 90%
- Corrélation native logs/metrics/traces
- UI intégrée performante

**Inconvénients :**
- Migration "big bang" nécessaire
- Moins mature que la stack classique
- Dashboards Grafana à recréer ou adapter

### Option C : Victoria Metrics Stack Complète

Stack 100% Victoria Metrics Labs (VictoriaMetrics + VictoriaLogs + VictoriaTraces).

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Application                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenTelemetry Collector                          │
└────────┬───────────────────┬───────────────────────┬────────────────┘
         │                   │                       │
         ▼                   ▼                       ▼
┌─────────────────┐  ┌─────────────────┐   ┌─────────────────────────┐
│ VictoriaMetrics │  │ VictoriaLogs    │   │ VictoriaTraces (beta)   │
│ (métriques)     │  │ (logs)          │   │ (traces)                │
│ - Cluster mode  │  │ - Ingestion     │   │ - Compatible Jaeger     │
│ - PromQL++      │  │   haute perf    │   │                         │
└────────┬────────┘  └────────┬────────┘   └────────────┬────────────┘
         │                    │                         │
         └────────────────────┴──────────┬──────────────┘
                                         │
                                         ▼
                               ┌─────────────────┐
                               │     Grafana     │
                               │  (Unified view) │
                               └─────────────────┘
```

---

## 4. Comparaison des Options

| Critère | Option A (Hybride) | Option B (OpenObserve) | Option C (Victoria) |
|---------|-------------------|------------------------|---------------------|
| **Complexité migration** | Faible | Moyenne | Moyenne |
| **Nb services** | 5-6 | 2-3 | 4-5 |
| **Maturité** | Haute | Moyenne | Haute (metrics), Beta (traces) |
| **Performance** | Excellente | Très bonne | Excellente |
| **Coût storage** | Moyen | Très faible | Faible |
| **Scalabilité** | Excellente | Excellente | Excellente |
| **PromQL support** | 100% | Partiel | 100%+ |
| **Dashboards Grafana** | Conservés | À adapter | Conservés |

---

## 5. Recommandation

### Court terme (Phase 1) - 2 semaines
**→ Adopter Victoria Metrics en remplacement de Prometheus**

- Migration transparente (100% compatible PromQL)
- Dashboards Grafana inchangés
- Gain immédiat en performance et ressources
- Zéro changement côté application

### Moyen terme (Phase 2) - 1 mois
**→ Évaluer OpenObserve pour les logs**

- POC en parallèle d'OpenSearch
- Comparer coût storage et performance queries
- Décision basée sur les résultats

### Long terme (Phase 3) - 3 mois
**→ Stack unifiée selon résultats POC**

- Si OpenObserve convient : migration logs + potentiellement métriques
- Si besoin full-text avancé : conserver OpenSearch optimisé

---

## 6. Fichiers de Configuration

Les configurations pour chaque option sont disponibles dans :

- `docker-compose.scalable.yml` - Stack hybride recommandée
- `victoria-metrics/` - Configuration Victoria Metrics
- `openobserve/` - Configuration OpenObserve
- `otel-collector-config/config-scalable.yaml` - OTel enrichi

---

## 7. Métriques de Succès

| Métrique | Baseline Actuelle | Cible |
|----------|-------------------|-------|
| RAM Prometheus/VM | 2 GB | < 500 MB |
| Latence query P99 | 500ms | < 50ms |
| Storage 30 jours | 50 GB | < 15 GB |
| Temps démarrage stack | 45s | < 20s |
| Nombre de services | 8 | 5-6 |

---

*Document généré le 2025-12-26 - AI Monitoring Platform v4.0*
