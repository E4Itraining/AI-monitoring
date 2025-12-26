# Runbook Opérationnel - AI Monitoring Platform

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Alertes et Résolutions](#alertes-et-résolutions)
3. [Procédures de Dépannage](#procédures-de-dépannage)
4. [Maintenance](#maintenance)

---

## Vue d'ensemble

### Architecture
```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   AI App    │────▶│ OTEL Collector│────▶│   Tempo    │
│  (FastAPI)  │     │              │     │  (Traces)  │
└─────────────┘     └──────────────┘     └────────────┘
       │                   │
       │                   ▼
       │            ┌────────────┐     ┌──────────────┐
       │            │ Prometheus │────▶│ AlertManager │
       │            │ (Metrics)  │     │  (Alerting)  │
       │            └────────────┘     └──────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌────────────┐
│ Fluent Bit  │────▶│ OpenSearch │
│   (Logs)    │     │   (Logs)   │
└─────────────┘     └────────────┘
       │                   │
       └───────────┬───────┘
                   ▼
            ┌────────────┐
            │  Grafana   │
            │ (Dashboard)│
            └────────────┘
```

### Ports des Services
| Service | Port | Description |
|---------|------|-------------|
| AI App | 8000 | Application principale |
| Prometheus | 9090 | Interface de métriques |
| AlertManager | 9093 | Interface d'alerting |
| Grafana | 3000 | Dashboards |
| Tempo | 3200 | Tracing API |
| OpenSearch | 9200 | Logs API |
| OpenSearch Dashboards | 5601 | Interface logs |
| OTEL Collector | 4317/4318 | OTLP gRPC/HTTP |
| Fluent Bit | 2020 | Metrics |

---

## Alertes et Résolutions

### AI Quality Score Low

**Alerte**: `AIQualityScoreLow`
**Sévérité**: Warning
**Seuil**: Score < 0.6 pendant 5 minutes

#### Symptômes
- Score de qualité des réponses AI dégradé
- Potentiellement plus d'hallucinations
- Feedback utilisateur négatif

#### Investigation
```bash
# Vérifier les métriques de qualité
curl -s http://localhost:9090/api/v1/query?query=ai_response_quality_score

# Vérifier le taux d'hallucinations
curl -s http://localhost:9090/api/v1/query?query=rate(ai_hallucination_events_total[5m])

# Examiner les logs récents
curl -s http://localhost:9200/ai-logs-*/_search?q=level:error
```

#### Résolution
1. Vérifier si le modèle AI sous-jacent a des problèmes
2. Examiner les prompts récents pour détecter des patterns problématiques
3. Vérifier le drift sémantique des entrées
4. Si nécessaire, augmenter les guardrails

---

### AI Quality Score Critical

**Alerte**: `AIQualityScoreCritical`
**Sévérité**: Critical
**Seuil**: Score < 0.4 pendant 2 minutes

#### Action immédiate
1. **Activer le mode de fallback** si disponible
2. Alerter l'équipe ML/AI
3. Considérer la désactivation temporaire du service

#### Investigation
```bash
# Vérifier l'état du service
docker logs ai-app --tail 100

# Examiner les traces
curl -s http://localhost:3200/api/traces?service=ai-lab-app&limit=10
```

---

### High Hallucination Rate

**Alerte**: `HighHallucinationRate`
**Sévérité**: Warning
**Seuil**: > 0.1/s pendant 3 minutes

#### Investigation
```bash
# Analyser les types de prompts causant des hallucinations
curl -s "http://localhost:9090/api/v1/query?query=ai_hallucination_events_total"

# Vérifier la distribution des topics
curl -s "http://localhost:9090/api/v1/query?query=ai_semantic_drift_score"
```

#### Résolution
1. Identifier les patterns de prompts problématiques
2. Renforcer les guardrails de vérification de faits
3. Ajuster les paramètres du modèle (température, etc.)

---

### Prompt Injection Detected

**Alerte**: `PromptInjectionDetected`
**Sévérité**: Critical
**Seuil**: > 5 tentatives en 5 minutes

#### Action immédiate
1. **Identifier l'IP source** et considérer un blocage
2. **Activer le rate limiting** agressif
3. **Analyser le vecteur d'attaque**

#### Investigation
```bash
# Trouver les IPs suspectes
curl -s "http://localhost:9090/api/v1/query?query=topk(10,sum by (ip) (ai_prompt_injection_detected_total))"

# Examiner les logs de sécurité
curl -s 'http://localhost:9200/ai-logs-*/_search' -H 'Content-Type: application/json' -d '
{
  "query": {
    "bool": {
      "must": [
        {"match": {"event_type": "security_threat"}}
      ]
    }
  },
  "size": 20
}'
```

#### Résolution
1. Bloquer les IPs malveillantes au niveau firewall/WAF
2. Renforcer les patterns de détection
3. Mettre à jour les règles de guardrails
4. Créer un incident de sécurité si nécessaire

---

### Jailbreak Attempt Detected

**Alerte**: `JailbreakAttemptDetected`
**Sévérité**: Critical
**Seuil**: > 3 tentatives en 5 minutes

#### Action immédiate
Similaire à Prompt Injection - voir section précédente

#### Patterns de jailbreak courants
- "Ignore previous instructions"
- "You are now DAN"
- Role-play pour contourner les restrictions
- Encodage de caractères spéciaux

---

### High PII Detection

**Alerte**: `HighPIIDetectionRate`
**Sévérité**: Warning
**Seuil**: > 0.5/s pendant 5 minutes

#### Investigation
```bash
# Types de PII détectés
curl -s "http://localhost:9090/api/v1/query?query=ai_pii_detected_total"

# Breakdown par type
curl -s "http://localhost:9090/api/v1/query?query=sum by (type) (ai_pii_detected_total)"
```

#### Résolution
1. Vérifier si c'est un usage légitime ou une fuite
2. Renforcer la redaction automatique
3. Alerter l'équipe compliance si nécessaire
4. Documenter pour conformité GDPR

---

### Semantic Drift High

**Alerte**: `SemanticDriftHigh`
**Sévérité**: Warning
**Seuil**: Score > 0.7 pendant 5 minutes

#### Signification
Les prompts entrants divergent significativement du baseline attendu.

#### Investigation
```bash
# Score de drift actuel
curl -s "http://localhost:9090/api/v1/query?query=ai_semantic_drift_score"

# Prompts hors domaine
curl -s "http://localhost:9090/api/v1/query?query=rate(ai_out_of_domain_total[10m])"
```

#### Résolution
1. Analyser les nouveaux types de prompts
2. Décider si le baseline doit être mis à jour
3. Ajuster les guardrails out-of-domain si nécessaire

---

### Error Budget Burn Rate

**Alerte**: `ErrorBudgetBurnRateHigh` / `ErrorBudgetBurnRateCritical`
**Sévérités**: Warning (>2x) / Critical (>10x)

#### Signification
- **1x** = consommation normale du budget d'erreurs
- **2x** = le budget sera épuisé 2x plus vite
- **10x** = situation critique, SLO en danger

#### Investigation
```bash
# Burn rate actuel
curl -s "http://localhost:9090/api/v1/query?query=ai_error_budget_burn_rate"

# Taux d'erreurs
curl -s "http://localhost:9090/api/v1/query?query=rate(ai_requests_error_total[5m])/rate(ai_requests_total[5m])"
```

#### Résolution
1. Identifier la source des erreurs
2. Réduire la charge si nécessaire
3. Déployer un fix ou rollback
4. Communiquer avec les stakeholders sur l'impact SLO

---

### Service Down

**Alerte**: `ServiceDown`
**Sévérité**: Critical
**Délai**: 1 minute

#### Action immédiate
```bash
# Vérifier l'état des containers
docker ps -a

# Vérifier les logs du service
docker logs ai-app --tail 200

# Vérifier les ressources
docker stats --no-stream
```

#### Procédure de recovery
```bash
# Redémarrer le service
docker-compose restart app

# Si échec, reconstruire
docker-compose up -d --build app

# Vérifier la santé
curl http://localhost:8000/health
```

---

### High Error Rate

**Alerte**: `HighErrorRate` / `HighErrorRateCritical`
**Seuils**: >5% (warning) / >10% (critical)

#### Investigation
```bash
# Distribution des erreurs par type
curl -s "http://localhost:9090/api/v1/query?query=sum by (error_type) (ai_requests_error_total)"

# Logs d'erreurs récents
docker logs ai-app 2>&1 | grep -i error | tail -50
```

---

### GDPR Compliance Low

**Alerte**: `GDPRComplianceLow`
**Sévérité**: Warning
**Seuil**: Score < 0.8

#### Implications
- Risque de non-conformité GDPR
- Potentielles fuites de données personnelles

#### Actions
1. Revoir les détections PII récentes
2. Vérifier que la redaction fonctionne
3. Contacter le DPO si nécessaire
4. Documenter l'incident

---

## Procédures de Dépannage

### Le service ne démarre pas

```bash
# 1. Vérifier les logs de démarrage
docker-compose logs app

# 2. Vérifier les dépendances
docker-compose ps

# 3. Vérifier les ressources
df -h
free -m

# 4. Reconstruire si nécessaire
docker-compose down
docker-compose build --no-cache app
docker-compose up -d
```

### Prometheus ne collecte pas les métriques

```bash
# 1. Vérifier les targets
curl http://localhost:9090/api/v1/targets

# 2. Vérifier la config
docker exec prometheus cat /etc/prometheus/prometheus.yml

# 3. Recharger la config
curl -X POST http://localhost:9090/-/reload
```

### Les alertes ne sont pas envoyées

```bash
# 1. Vérifier AlertManager
curl http://localhost:9093/-/healthy

# 2. Vérifier les alertes actives
curl http://localhost:9093/api/v2/alerts

# 3. Vérifier les silences
curl http://localhost:9093/api/v2/silences
```

### Les traces sont manquantes

```bash
# 1. Vérifier Tempo
curl http://localhost:3200/ready

# 2. Vérifier OTEL Collector
docker logs otel-collector --tail 100

# 3. Vérifier l'export
curl http://localhost:8888/metrics | grep otelcol_exporter
```

---

## Maintenance

### Backup des données

```bash
# Sauvegarder Prometheus
docker run --rm -v prometheus-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz /data

# Sauvegarder OpenSearch
curl -X PUT "localhost:9200/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backup"
  }
}'
curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d)?wait_for_completion=true"
```

### Rotation des logs

```bash
# Les logs dans /logs sont collectés par Fluent Bit
# Configurer la rotation dans fluent-bit.conf ou via logrotate

# Vérifier l'espace disque des logs
du -sh logs/
```

### Mise à jour des services

```bash
# 1. Mettre à jour .env avec les nouvelles versions
# 2. Pull des nouvelles images
docker-compose pull

# 3. Redémarrer progressivement
docker-compose up -d --no-deps tempo
docker-compose up -d --no-deps prometheus
docker-compose up -d --no-deps app
```

### Nettoyage

```bash
# Supprimer les images non utilisées
docker image prune -a

# Supprimer les volumes orphelins
docker volume prune

# Nettoyer les logs anciens
find logs/ -name "*.log" -mtime +7 -delete
```

---

## Contacts

| Équipe | Responsabilité | Contact |
|--------|----------------|---------|
| SRE | Infrastructure | sre@example.com |
| ML/AI | Modèles et qualité | ml-team@example.com |
| Security | Incidents sécurité | security@example.com |
| Compliance | GDPR/AI Act | compliance@example.com |

---

*Dernière mise à jour: Décembre 2024*
