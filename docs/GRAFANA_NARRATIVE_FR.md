# Narratif Grafana - AI Trustworthiness Observatory

> **Disponible en :** [English](GRAFANA_NARRATIVE.md) | [Français](GRAFANA_NARRATIVE_FR.md)

## Notre Vision

Transformer l'observabilité des systèmes IA en un **levier stratégique** qui garantit la qualité, la sécurité, la conformité et l'efficience économique de vos déploiements d'intelligence artificielle.

---

## Ce Que Nous Faisons

### Une Plateforme d'Observabilité Complète pour l'IA

Nous avons construit un **observatoire unifié** qui surveille en temps réel tous les aspects critiques d'un système IA en production :

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI TRUSTWORTHINESS SUITE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   📊 QUALITÉ        🔒 SÉCURITÉ       📜 CONFORMITÉ              │
│   ─────────         ─────────        ───────────                 │
│   • Score qualité   • Injection      • RGPD                     │
│   • Hallucinations  • Jailbreak      • AI Act                   │
│   • Cohérence       • PII Detection  • Audit Trail              │
│                                                                  │
│   💰 COÛTS          ⚡ PERFORMANCE    🌱 DURABILITÉ              │
│   ─────────         ───────────      ───────────                 │
│   • Tokens          • Latence P99    • Tokens/requête           │
│   • EUR/requête     • Throughput     • Efficience               │
│   • Anomalies       • SLO/SLI        • Optimisation             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Technique

Notre stack repose sur des technologies open-source éprouvées :

| Composant | Rôle | Valeur Ajoutée |
|-----------|------|----------------|
| **Grafana 11** | Visualisation unifiée | 4 dashboards métier dédiés |
| **Prometheus/Victoria Metrics** | Stockage métriques | 7x plus efficace en RAM |
| **Tempo** | Traces distribuées | Corrélation bout-en-bout |
| **OpenSearch** | Logs structurés | Recherche full-text |
| **AlertManager** | Alerting intelligent | 7 canaux par équipe |

---

## Ce Que Nous Mesurons

### 50+ Métriques Organisées en 6 Domaines

#### 1. 📊 Qualité des Réponses IA

| Métrique | Description | Seuil Cible |
|----------|-------------|-------------|
| `ai_response_quality_score` | Score de qualité global (0-1) | > 0.80 |
| `ai_hallucination_events_total` | Détection d'hallucinations | < 1% |
| `ai_coherence_score` | Cohérence contextuelle | > 0.85 |
| `ai_user_satisfaction_score` | Satisfaction utilisateur (1-5) | > 4.0 |

**Impact** : Garantir des réponses fiables et pertinentes qui renforcent la confiance utilisateur.

#### 2. 🔒 Sécurité & Protection

| Métrique | Description | Action |
|----------|-------------|--------|
| `ai_prompt_injection_attempts_total` | Tentatives d'injection | Blocage automatique |
| `ai_jailbreak_attempts_total` | Tentatives de contournement | Alerte immédiate |
| `ai_pii_detected_total` | Données personnelles détectées | Masquage/Blocage |
| `ai_toxicity_events_total` | Contenus toxiques | Filtrage |

**8 types de PII détectés** : email, téléphone, carte bancaire, SSN, IBAN, IP, date de naissance, nom.

#### 3. 📜 Conformité Réglementaire

| Métrique | Description | Réglementation |
|----------|-------------|----------------|
| `ai_gdpr_compliance_score` | Score conformité RGPD | RGPD |
| `ai_compliance_score{category="ai_act"}` | Score AI Act | AI Act |
| `ai_trust_index` | Indice de confiance global | Multi-cadre |
| `ai_risk_level_gauge` | Niveau de risque (low→critical) | AI Act Article 6 |

#### 4. 💰 Économie & Coûts

| Métrique | Description | Optimisation |
|----------|-------------|--------------|
| `ai_tokens_input_total` | Tokens d'entrée consommés | Par modèle |
| `ai_tokens_output_total` | Tokens de sortie générés | Par modèle |
| `ai_cost_estimated_eur_total` | Coût cumulé en EUR | Temps réel |
| Coût/requête | EUR par requête | Alertes anomalies |

#### 5. ⚡ Performance & SLO

| Métrique | Description | SLO |
|----------|-------------|-----|
| `ai_latency_seconds` (P99) | Latence 99e percentile | < 1000ms |
| `ai_requests_error_total` | Taux d'erreur | < 0.5% |
| `ai_slo_compliance_ratio` | Respect global SLO | > 99.5% |
| `ai_error_budget_burn_rate` | Vélocité budget erreur | < 1.0 |

#### 6. 🔄 Dérive Sémantique

| Métrique | Description | Dimension |
|----------|-------------|-----------|
| `ai_input_drift_score{dimension="topic"}` | Dérive thématique | Sujet |
| `ai_input_drift_score{dimension="domain"}` | Dérive de domaine | Expertise |
| `ai_input_drift_score{dimension="complexity"}` | Dérive de complexité | Difficulté |
| `ai_out_of_domain_total` | Prompts hors-domaine | Périmètre |

---

## L'Impact

### Impact Technique

| Avant | Après | Gain |
|-------|-------|------|
| Incidents non détectés | Détection proactive < 5min | **-80% MTTR** |
| Debugging aveugle | Traces corrélées E2E | **-60% temps debug** |
| Métriques manuelles | Automatisation complète | **100% couverture** |
| Alertes bruyantes | Alerting intelligent routé | **-70% faux positifs** |

### Impact Business

| Dimension | Bénéfice | Mesure |
|-----------|----------|--------|
| **Confiance client** | Réponses IA vérifiées | Trust Index > 0.85 |
| **Réduction coûts** | Optimisation tokens | -15-30% facture LLM |
| **Time-to-market** | Déploiement confiant | +50% vélocité release |
| **Risque légal** | Conformité prouvable | Audit trail complet |

### Impact Conformité

| Réglementation | Exigence | Couverture |
|----------------|----------|------------|
| **RGPD** | Protection données personnelles | PII Detection + Masquage |
| **AI Act** | Gestion des risques | Classification + Monitoring |
| **AI Act** | Transparence | Audit trail + Traçabilité |
| **AI Act** | Documentation | Dashboards + Export |

### Impact Environnemental (GreenOps)

| Métrique | Optimisation | Impact |
|----------|--------------|--------|
| Tokens/requête | Réduction prompt verbeux | -20% consommation |
| Requêtes inutiles | Cache intelligent | -30% appels API |
| Modèle adapté | Right-sizing modèle | -40% compute |

---

## Parcours par Persona

### 🔧 Persona TECH (SRE / DevOps / ML Engineer)

**Objectif** : Maintenir la fiabilité et les performances du système IA en production.

#### Dashboard Principal : `AI Reliability Overview`

```
┌─────────────────────────────────────────────────────────────────┐
│                    🔧 VUE SRE / TECH                             │
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
│  🔔 Alertes actives: 0 Critical | 1 Warning                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Workflow Quotidien

1. **Morning Check** (5 min)
   - Vérifier le SLO dashboard : Budget erreur consommé ?
   - Scanner les alertes overnight
   - Contrôler la latence P99 trend

2. **Incident Response**
   - Cliquer sur l'alerte → Drill-down vers traces Tempo
   - Corréler avec les logs OpenSearch
   - Identifier le scénario problématique (drift, load, injection)

3. **Capacity Planning**
   - Analyser `ai_inflight_requests` pour anticiper le scaling
   - Monitorer `ai_rate_limit_events_total` pour ajuster les limites

#### Alertes Configurées

| Alerte | Seuil | Action |
|--------|-------|--------|
| `HighLatencyP99` | > 1000ms pendant 5min | Investigation perf |
| `ErrorBudgetBurnRateHigh` | > 2x normal | Review déploiements |
| `ServiceDown` | 0 requête pendant 2min | Incident majeur |

---

### 💼 Persona BUSINESS (Product Owner / Manager)

**Objectif** : Comprendre la valeur et les risques business de l'IA déployée.

#### Dashboard Principal : `AI Trustworthiness Suite v4.0`

```
┌─────────────────────────────────────────────────────────────────┐
│                    💼 VUE BUSINESS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    TRUST INDEX                            │   │
│  │                                                           │   │
│  │              ████████████████░░░░  0.87 / 1.0            │   │
│  │                                                           │   │
│  │   ✅ Qualité: OK    ✅ Sécurité: OK    ⚠️ Coûts: Élevés  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Satisfaction│  │ Coût Jour   │  │ Conversations│             │
│  │    ⭐ 4.2   │  │   €47.50    │  │     1,234    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  📈 Tendance satisfaction: +5% vs semaine dernière              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### KPIs Clés

| KPI | Description | Cible |
|-----|-------------|-------|
| **Trust Index** | Indice de confiance global | > 0.85 |
| **User Satisfaction** | Note moyenne utilisateurs | > 4.0/5 |
| **Coût/Conversation** | Coût moyen par échange | < €0.05 |
| **Hallucination Rate** | % réponses douteuses | < 1% |

#### Questions Auxquelles le Dashboard Répond

- *"L'IA répond-elle correctement ?"* → Quality Score + Satisfaction
- *"Combien ça coûte ?"* → Cost panels + Trend
- *"Est-ce risqué ?"* → Risk Level + Security Score
- *"Les utilisateurs sont-ils satisfaits ?"* → Feedback Score

#### Rapport Hebdomadaire Auto-générable

```
📊 RAPPORT HEBDOMADAIRE AI - Semaine 42

✅ Trust Index moyen: 0.87 (+2%)
✅ Satisfaction utilisateur: 4.2/5 (+0.1)
✅ Disponibilité: 99.8%
⚠️ Coût total: €347 (+15% vs budget)
✅ Incidents sécurité: 0 critique
```

---

### 📜 Persona COMPLIANCE (DPO / Legal / Risk Manager)

**Objectif** : Garantir la conformité réglementaire et documenter la gouvernance IA.

#### Dashboard Principal : Panels dédiés dans `AI Trustworthiness Suite`

```
┌─────────────────────────────────────────────────────────────────┐
│                    📜 VUE COMPLIANCE                             │
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
│  │              PII DETECTION (7 derniers jours)            │    │
│  │                                                          │    │
│  │  Email: 45 détectés | 45 masqués | 0 fuite              │    │
│  │  Phone: 12 détectés | 12 masqués | 0 fuite              │    │
│  │  IBAN:  3 détectés  |  3 bloqués | 0 fuite              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  📋 Audit Events cette semaine: 12,456 (100% tracés)            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Exigences Réglementaires Couvertes

##### RGPD (Règlement Général sur la Protection des Données)

| Article | Exigence | Couverture |
|---------|----------|------------|
| Art. 5 | Minimisation des données | PII Detection + Masquage |
| Art. 17 | Droit à l'effacement | Conversation deletion API |
| Art. 30 | Registre des traitements | Audit trail complet |
| Art. 33 | Notification violations | Alertes temps réel |

##### AI Act (Règlement Européen sur l'IA)

| Article | Exigence | Couverture |
|---------|----------|------------|
| Art. 9 | Gestion des risques | `ai_risk_level_gauge` |
| Art. 12 | Tenue de registres | OpenSearch logs + Trace IDs |
| Art. 13 | Transparence | Dashboards accessibles |
| Art. 14 | Contrôle humain | Guardrails configurables |

#### Alertes Compliance

| Alerte | Déclencheur | Escalade |
|--------|-------------|----------|
| `GDPRComplianceLow` | Score < 0.8 | compliance@example.com |
| `AIActHighRisk` | Niveau critique | DPO + Legal |
| `HighPIIDetectionRate` | > 0.5/sec | Investigation immédiate |

#### Export Audit

```bash
# Export des événements d'audit pour inspection
curl "http://opensearch:9200/ai-logs/_search?q=event_type:audit" \
  -H "Content-Type: application/json" > audit_export.json
```

---

### 🌱 Persona GREENOPS (Sustainability / FinOps / Efficiency)

**Objectif** : Optimiser l'empreinte environnementale et économique de l'IA.

#### Dashboard Focus : Panels Coûts & Efficience

```
┌─────────────────────────────────────────────────────────────────┐
│                    🌱 VUE GREENOPS                               │
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
│  │   ▼ vs hier  │  │   ⚠️ élevé   │  │   ✅ bon     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  🌍 Estimation CO2: ~2.3 kg/jour (basé sur usage cloud)         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Métriques d'Efficience

| Métrique | Formule | Objectif |
|----------|---------|----------|
| **Token Efficiency** | Tokens utiles / Tokens totaux | > 85% |
| **Cost per Value** | Coût / Satisfaction | Minimiser |
| **Waste Ratio** | Requêtes échouées / Total | < 5% |
| **Model Right-sizing** | Qualité / Coût modèle | Optimiser |

#### Stratégies d'Optimisation Identifiables

1. **Prompt Engineering**
   - Monitorer `ai_tokens_input_total` par scénario
   - Identifier les prompts verbeux (> 2000 tokens)
   - Objectif : -20% tokens input

2. **Caching Intelligent**
   - Analyser les patterns de requêtes similaires
   - Implémenter cache sémantique
   - Objectif : -30% appels API

3. **Model Selection**
   - Comparer qualité/coût par modèle via labels
   - Router requêtes simples vers modèles légers
   - Objectif : -40% coût sans perte qualité

4. **Rate Limiting Proactif**
   - Monitorer `ai_rate_limit_events_total`
   - Éviter les pics de consommation
   - Lisser la charge

#### Dashboard FinOps Recommandé

```
Rate(ai_cost_estimated_eur_total[1h]) * 24 * 30  → Projection mensuelle
Rate(ai_tokens_input_total[1d]) / count(ai_requests_total[1d]) → Tokens/req
```

---

## Synthèse des Dashboards par Persona

| Persona | Dashboard Principal | Fréquence | Métriques Clés |
|---------|---------------------|-----------|----------------|
| **🔧 Tech** | AI Reliability + SLO | Continue | Latency, Errors, SLO |
| **💼 Business** | AI Trustworthiness Suite | Quotidien | Trust Index, Satisfaction, Cost |
| **📜 Compliance** | Panels Compliance | Hebdo/Audit | GDPR Score, PII, Risk Level |
| **🌱 GreenOps** | Panels Cost + Custom | Mensuel | Tokens, EUR/req, Efficiency |

---

## Mise en Route

### Accès Rapide

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| AlertManager | http://localhost:9093 | - |

### Premiers Pas par Persona

1. **Tech** : Ouvrir `AI Reliability Overview` → Vérifier SLO compliance
2. **Business** : Ouvrir `AI Trustworthiness Suite` → Lire Trust Index
3. **Compliance** : Filtrer panels GDPR → Exporter audit logs
4. **GreenOps** : Créer dashboard custom avec métriques coût

---

## Conclusion

Cette plateforme d'observabilité AI transforme les données brutes de monitoring en **insights actionnables** pour chaque partie prenante. En unifiant qualité, sécurité, conformité et efficience dans un seul observatoire, nous permettons à chaque persona de prendre des décisions éclairées basées sur des données fiables et en temps réel.

> *"Ce qui ne se mesure pas ne peut pas s'améliorer."* - Peter Drucker

Avec notre AI Trustworthiness Observatory, chaque aspect de votre IA en production est non seulement mesuré, mais optimisable.
