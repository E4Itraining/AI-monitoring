# AI Observability Lab - OSMC Edition

Prerequisites:
- Docker + Docker Compose
- Free ports: 8000, 3000, 9090, 3200, 9200, 5601

Start the stack:
- Run: docker compose up --build

Main services:
- App: http://localhost:8000
- Grafana: http://localhost:3000 (admin / admin)
- Prometheus: http://localhost:9090
- Tempo: http://localhost:3200
- OpenSearch Dashboards: http://localhost:5601
