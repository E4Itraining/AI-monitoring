# Guide de Migration - Architecture Scalable

## Vue d'ensemble

Ce guide explique comment migrer de l'architecture actuelle vers la nouvelle stack scalable.

## Comparaison des Stacks

| Composant | Stack Actuelle | Stack Scalable |
|-----------|----------------|----------------|
| Métriques | Prometheus | **Victoria Metrics** |
| Traces | Tempo (local) | Tempo (optimisé) |
| Logs | OpenSearch | OpenSearch + **OpenObserve** |
| Collecte | OTel Collector | OTel Collector (enrichi) |
| Shipper | Fluent-bit | Fluent-bit (dual output) |

## Étapes de Migration

### Phase 1: Préparation

```bash
# 1. Sauvegarder les données actuelles
docker-compose exec prometheus promtool tsdb dump /prometheus > prometheus-backup.json

# 2. Exporter les dashboards Grafana
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/ai-trustworthiness \
  | jq '.dashboard' > dashboard-backup.json

# 3. Arrêter la stack actuelle
docker-compose down
```

### Phase 2: Démarrage Stack Scalable

```bash
# 1. Démarrer la nouvelle stack
docker-compose -f docker-compose.scalable.yml up -d

# 2. Vérifier les services
docker-compose -f docker-compose.scalable.yml ps

# 3. Tester les endpoints
curl http://localhost:8428/health        # Victoria Metrics
curl http://localhost:5080/healthz       # OpenObserve
curl http://localhost:3200/ready         # Tempo
```

### Phase 3: Configuration Grafana

```bash
# Copier les nouvelles datasources
cp grafana/provisioning/datasources/datasources-scalable.yml.template \
   grafana/provisioning/datasources/datasources.yml

# Redémarrer Grafana
docker-compose -f docker-compose.scalable.yml restart grafana
```

### Phase 4: Validation

```bash
# Envoyer des métriques de test
curl -X POST http://localhost:8428/api/v1/write \
  -d 'test_metric{job="test"} 42'

# Vérifier dans Victoria Metrics
curl 'http://localhost:8428/api/v1/query?query=test_metric'

# Vérifier les logs dans OpenObserve
curl -u admin@ai-monitoring.local:ComplexPass123! \
  'http://localhost:5080/api/default/ai-logs/_search'
```

## Points d'Accès

| Service | URL | Credentials |
|---------|-----|-------------|
| Victoria Metrics | http://localhost:8428 | - |
| OpenObserve | http://localhost:5080 | admin@ai-monitoring.local / ComplexPass123! |
| Tempo | http://localhost:3200 | - |
| Grafana | http://localhost:3000 | admin / admin |
| OpenSearch | http://localhost:9200 | - |
| App | http://localhost:8000 | - |

## Rollback

En cas de problème, retour à la stack originale :

```bash
# Arrêter la stack scalable
docker-compose -f docker-compose.scalable.yml down

# Redémarrer la stack originale
docker-compose up -d
```

## Commandes Utiles

```bash
# Logs Victoria Metrics
docker logs victoria-metrics -f

# Logs OpenObserve
docker logs openobserve -f

# Métriques OTel Collector
curl http://localhost:8888/metrics

# Status Fluent-bit
curl http://localhost:2020/api/v1/health
```

## Performance Attendue

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| RAM métriques | 2 GB | ~300 MB | 7x |
| Latence query | 500ms | ~50ms | 10x |
| Storage/30j | 50 GB | ~15 GB | 3x |
| Startup time | 45s | ~20s | 2x |
