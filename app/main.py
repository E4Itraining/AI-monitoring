import time
import random
import json
import logging
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from opentelemetry import trace

# --- OpenTelemetry SDK (TRACES → otel-collector en gRPC) --------------------
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# -------------------------------------------------------------------
# Logging JSON vers /logs/app.log (pour Fluent Bit / OpenSearch)
# -------------------------------------------------------------------
logger = logging.getLogger("ai_app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    try:
        file_handler = logging.FileHandler("/logs/app.log")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)
    except Exception:
        # fallback stdout uniquement si /logs n'existe pas
        pass

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stdout_handler)

# -------------------------------------------------------------------
# OpenTelemetry tracer CONFIG (important pour Tempo)
# -------------------------------------------------------------------
resource = Resource(
    attributes={
        "service.name": "ai-demo-app",
        "service.namespace": "ai-lab",
        "service.version": "3.0.0",
        "service.instance.id": "ai-demo-app-1",
    }
)

trace_provider = TracerProvider(resource=resource)

# Exporter OTLP gRPC vers l'OTel Collector
otlp_exporter = OTLPSpanExporter(
    endpoint="otel-collector:4317",  # gRPC, PAS de /v1/traces
    insecure=True,
)

trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer("ai-demo-app")

# -------------------------------------------------------------------
# Prometheus metrics (v2, alignées avec les dashboards)
# -------------------------------------------------------------------

# Trafic global
ai_requests_total = Counter(
    "ai_requests_total",
    "Total number of AI requests",
    ["scenario"],
)

# Pour les dashboards : ai_requests_error_total
ai_requests_error_total = Counter(
    "ai_requests_error_total",
    "Total number of failed AI requests",
    ["scenario"],
)

# Histograms de latence (pour ai_latency_seconds_bucket)
ai_latency_seconds = Histogram(
    "ai_latency_seconds",
    "Latency of AI responses in seconds",
    ["scenario"],
)

# Histogram de qualité brute (utilisé en interne)
ai_response_quality_score = Histogram(
    "ai_response_quality_score",
    "Quality score of AI responses",
    ["scenario"],
)

# Gauge de qualité pour les dashboards (ai_quality_score)
ai_quality_score = Gauge(
    "ai_quality_score",
    "Aggregated quality score (0-1)",
)

# Coût total estimé (ai_cost_estimated_eur_total)
ai_cost_estimated_eur_total = Counter(
    "ai_cost_estimated_eur_total",
    "Estimated total cost in EUR",
)

# Ancien compteur (conservé pour compatibilité)
ai_estimated_cost_eur_total = Counter(
    "ai_estimated_cost_eur_total",
    "Estimated total cost in EUR (legacy, per scenario)",
    ["scenario"],
)

# Hallucinations / policy breaches (ai_hallucination_events_total)
ai_hallucination_events_total = Counter(
    "ai_hallucination_events_total",
    "Detected hallucination / policy breach events",
    ["detector"],
)

# Ancien compteur (on l'alimente en parallèle)
ai_hallucination_suspected_total = Counter(
    "ai_hallucination_suspected_total",
    "Total number of suspected hallucinations",
    ["scenario"],
)

# Toxicité / unsafe_outputs (ai_toxicity_events_total)
ai_toxicity_events_total = Counter(
    "ai_toxicity_events_total",
    "Detected toxic / unsafe outputs",
    ["severity"],
)

# Réponses risquées (legacy)
ai_risky_responses_total = Counter(
    "ai_risky_responses_total",
    "Total number of risky AI responses",
    ["scenario"],
)

# Drift factor pour les dashboards (ai_input_drift_score)
ai_input_drift_score = Gauge(
    "ai_input_drift_score",
    "Input drift score (0-1) per scenario",
    ["scenario"],
)

# Legacy drift gauge (alias interne)
ai_drift_factor = Gauge(
    "ai_drift_factor",
    "Current drift factor (0-1) per scenario (legacy)",
    ["scenario"],
)

# Trust / compliance synthétique (0–1)
ai_trust_index = Gauge(
    "ai_trust_index",
    "Synthetic trust/compliance index (0-1) per scenario",
    ["scenario"],
)

# In-flight requests (ai_inflight_requests)
ai_inflight_requests = Gauge(
    "ai_inflight_requests",
    "Number of in-flight AI requests",
    ["endpoint"],
)

# Rate limiting events (ai_rate_limit_events_total)
ai_rate_limit_events_total = Counter(
    "ai_rate_limit_events_total",
    "Number of rate limit / throttling events",
    ["reason"],
)

# Tokens in/out
ai_tokens_input_total = Counter(
    "ai_tokens_input_total",
    "Total input tokens processed",
    ["model"],
)

ai_tokens_output_total = Counter(
    "ai_tokens_output_total",
    "Total output tokens produced",
    ["model"],
)

# SLI / SLO metrics
ai_sli_latency_requests_total = Counter(
    "ai_sli_latency_requests_total",
    "Number of requests evaluated for latency SLI",
)

ai_sli_latency_violations_total = Counter(
    "ai_sli_latency_violations_total",
    "Number of latency SLI violations",
)

ai_sli_quality_requests_total = Counter(
    "ai_sli_quality_requests_total",
    "Number of requests evaluated for quality SLI",
)

ai_sli_quality_violations_total = Counter(
    "ai_sli_quality_violations_total",
    "Number of quality SLI violations",
)

ai_slo_error_budget_burn_rate = Gauge(
    "ai_slo_error_budget_burn_rate",
    "Instantaneous error budget burn rate (0..1)",
)

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(title="AI Reliability / Observability Demo")


class PredictRequest(BaseModel):
    prompt: str
    scenario: str = "baseline"  # "baseline", "drift", "latency-spike", ...


class PredictResponse(BaseModel):
    prompt: str
    scenario: str
    answer: str

    quality_score: float
    hallucination_suspected: bool
    estimated_cost_eur: float
    latency_ms: float

    # Bloc fiabilité / risque
    mode: str
    coherence: float
    hallucination: bool
    risk_flag: bool
    risk_reason: str
    ai_act_risk_level: str
    drift_factor: float


# -------------------------------------------------------------------
# Helpers de classification & estimation
# -------------------------------------------------------------------

def normalize_scenario(raw: str) -> tuple[str, str]:
    """
    Normalise la valeur de scenario pour les métriques & la simulation.

    Retourne (scenario_tag, mode_code)

    scenario_tag : utilisé dans les labels Prometheus
      → "baseline", "drift", "latency-spike", "prompt-injection",
         "high-risk", "toxic", "after-mitigation", "other"

    mode_code : pilote la simulation de latence / qualité
      → "nominal", "drift", "stress", "risky"
    """
    if not raw:
        return "baseline", "nominal"

    s = raw.strip().lower()

    if s in ("a", "baseline", "nominal"):
        return "baseline", "nominal"
    if s in ("after-mitigation", "mitigated"):
        return "after-mitigation", "nominal"
    if s in ("b", "drift"):
        return "drift", "drift"
    if s in ("c", "latency-spike", "stress"):
        return "latency-spike", "stress"
    if s in ("prompt-injection", "injection"):
        return "prompt-injection", "risky"
    if s in ("high-risk", "risk"):
        return "high-risk", "risky"
    if s in ("toxic",):
        return "toxic", "risky"

    # fallback
    return s, "nominal"


def estimate_tokens(prompt: str) -> tuple[int, int]:
    words = len(prompt.split())
    input_tokens = int(words * random.uniform(1.2, 1.8))
    output_tokens = int(words * random.uniform(0.8, 1.5))
    return input_tokens, output_tokens


# -------------------------------------------------------------------
# Endpoints basiques
# -------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# -------------------------------------------------------------------
# Simulation de réponse IA
# -------------------------------------------------------------------
def simulate_ai_response(prompt: str, scenario_tag: str, mode: str):
    # Latence simulée
    if mode == "nominal":
        base_latency = random.uniform(0.05, 0.15)
    elif mode == "drift":
        base_latency = random.uniform(0.1, 0.25)
    elif mode == "stress":
        base_latency = random.uniform(0.2, 0.6)
    elif mode == "risky":
        base_latency = random.uniform(0.15, 0.5)
    else:
        base_latency = random.uniform(0.1, 0.3)

    time.sleep(base_latency)

    # Qualité / hallucination selon scenario
    if scenario_tag in ("baseline", "after-mitigation"):
        quality = random.uniform(0.8, 0.95)
        hallucination_suspected = False
    elif scenario_tag == "drift":
        quality = random.uniform(0.4, 0.85)
        hallucination_suspected = random.random() < 0.3
    elif scenario_tag == "latency-spike":
        quality = random.uniform(0.6, 0.9)
        hallucination_suspected = random.random() < 0.2
    else:  # prompt-injection / high-risk / toxic / other
        quality = random.uniform(0.3, 0.8)
        hallucination_suspected = random.random() < 0.4

    base_cost = 0.0005 * len(prompt)
    if scenario_tag in ("latency-spike", "high-risk", "toxic"):
        base_cost *= 1.5
    estimated_cost = base_cost

    answer = f"Réponse simulée pour le scénario {scenario_tag} avec score {quality:.2f}."

    return answer, quality, hallucination_suspected, estimated_cost, base_latency


# -------------------------------------------------------------------
# Endpoint /predict
# -------------------------------------------------------------------
@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Normalisation du scenario
    scenario_tag, mode = normalize_scenario(req.scenario)
    prompt = req.prompt or ""
    endpoint = "/predict"
    model = "demo-medium"

    # Pré-crée les séries Prometheus pour ce scenario
    err_counter = ai_requests_error_total.labels(scenario=scenario_tag)
    hall_counter = ai_hallucination_suspected_total.labels(scenario=scenario_tag)
    risky_counter = ai_risky_responses_total.labels(scenario=scenario_tag)
    drift_gauge_legacy = ai_drift_factor.labels(scenario=scenario_tag)
    trust_gauge = ai_trust_index.labels(scenario=scenario_tag)
    drift_gauge = ai_input_drift_score.labels(scenario=scenario_tag)

    ai_requests_total.labels(scenario=scenario_tag).inc()
    ai_inflight_requests.labels(endpoint=endpoint).inc()

    start = time.time()

    with tracer.start_as_current_span("ai_predict") as span:
        span.set_attribute("ai.prompt_length", len(prompt))
        span.set_attribute("ai.scenario", scenario_tag)
        span.set_attribute("ai.mode", mode)

        try:
            answer, quality, hallucination_suspected, estimated_cost, sim_latency = simulate_ai_response(
                prompt, scenario_tag, mode
            )
            error = False
        except Exception as e:
            answer = "Erreur interne dans la simulation."
            quality = 0.0
            hallucination_suspected = False
            estimated_cost = 0.0
            sim_latency = 0.0
            error = True
            logger.error(json.dumps({"event": "error", "message": str(e)}, ensure_ascii=False))

        elapsed = time.time() - start
        latency_ms = elapsed * 1000.0

        # Estimation des tokens et du coût agrégé
        in_toks, out_toks = estimate_tokens(prompt)
        ai_tokens_input_total.labels(model=model).inc(in_toks)
        ai_tokens_output_total.labels(model=model).inc(out_toks)
        ai_cost_estimated_eur_total.inc(estimated_cost)
        ai_estimated_cost_eur_total.labels(scenario=scenario_tag).inc(estimated_cost)

        # -------------------------------------------------------------------
        # Évaluation fiabilité / risque (ANTI-NULL)
        # -------------------------------------------------------------------
        coherence = float(quality) if quality is not None else 0.0
        hallucination = bool(hallucination_suspected)

        # Drift factor (scénario)
        if scenario_tag in ("baseline", "after-mitigation"):
            drift_factor = 0.0
        elif scenario_tag == "drift":
            drift_factor = round(random.uniform(0.4, 1.0), 3)
        elif scenario_tag == "latency-spike":
            drift_factor = round(random.uniform(0.2, 0.6), 3)
        else:
            drift_factor = round(random.uniform(0.3, 0.9), 3)

        risk_flag = False
        risk_reason = "ok"

        if coherence < 0.65:
            risk_flag = True
            risk_reason = "low_coherence"

        if hallucination and not risk_flag:
            risk_flag = True
            risk_reason = "hallucination_detected"

        lowered = prompt.lower()
        if any(k in lowered for k in ["ignore", "règles", "regles", "bypass security"]):
            risk_flag = True
            risk_reason = "prompt_injection"

        # 6. AI Act risk level
        if not risk_flag:
            ai_act_risk_level = "low"
        elif risk_reason in ("low_coherence", "hallucination_detected"):
            ai_act_risk_level = "medium"
        elif risk_reason == "prompt_injection":
            ai_act_risk_level = "high"
        else:
            ai_act_risk_level = "medium"

        # --- Trust index synthétique (0–1) en fonction du niveau de risque ---
        if not risk_flag:
            trust_index = 1.0
        elif ai_act_risk_level == "medium":
            trust_index = 0.6
        elif ai_act_risk_level == "high":
            trust_index = 0.3
        else:
            trust_index = 0.5

        # -------------------------------------------------------------------
        # Alimentation métriques Prometheus
        # -------------------------------------------------------------------
        ai_latency_seconds.labels(scenario=scenario_tag).observe(elapsed)
        ai_response_quality_score.labels(scenario=scenario_tag).observe(quality)
        ai_quality_score.set(quality)

        # SLI/SLO latency
        ai_sli_latency_requests_total.inc()
        if elapsed > 1.0:
            ai_sli_latency_violations_total.inc()

        # SLI/SLO quality
        ai_sli_quality_requests_total.inc()
        if quality < 0.8:
            ai_sli_quality_violations_total.inc()

        # Burn rate simplifiée
        if scenario_tag in ("baseline", "after-mitigation"):
            burn = random.uniform(0.0, 0.1)
        elif scenario_tag in ("drift", "latency-spike"):
            burn = random.uniform(0.3, 0.7)
        else:
            burn = random.uniform(0.5, 1.0)
        ai_slo_error_budget_burn_rate.set(burn)

        # Toujours créer les séries, même quand il n'y a pas d'événement
        if error:
            err_counter.inc()
        else:
            err_counter.inc(0)

        if hallucination_suspected:
            hall_counter.inc()
            ai_hallucination_events_total.labels(detector="rule-engine").inc()
        else:
            hall_counter.inc(0)

        if risk_flag:
            risky_counter.inc()
        else:
            risky_counter.inc(0)

        # Toxicité : on déclenche pour certains scénarios / signaux
        if scenario_tag in ("toxic", "high-risk") or ai_act_risk_level == "high":
            ai_toxicity_events_total.labels(severity="high").inc()

        drift_gauge.set(drift_factor)
        drift_gauge_legacy.set(drift_factor)
        trust_gauge.set(trust_index)

        # Fin in-flight
        ai_inflight_requests.labels(endpoint=endpoint).dec()

        # -------------------------------------------------------------------
        # Attributs OTEL (Tempo)
        # -------------------------------------------------------------------
        span.set_attribute("ai.quality_score", float(quality))
        span.set_attribute("ai.hallucination_suspected", bool(hallucination_suspected))
        span.set_attribute("ai.estimated_cost_eur", float(estimated_cost))
        span.set_attribute("ai.latency_ms", float(latency_ms))

        span.set_attribute("ai.eval.mode", mode)
        span.set_attribute("ai.eval.coherence", float(coherence))
        span.set_attribute("ai.eval.hallucination", bool(hallucination))
        span.set_attribute("ai.eval.risk_flag", bool(risk_flag))
        span.set_attribute("ai.eval.risk_reason", risk_reason)
        span.set_attribute("ai.eval.ai_act_risk_level", ai_act_risk_level)
        span.set_attribute("ai.eval.drift_factor", float(drift_factor))
        span.set_attribute("ai.eval.trust_index", float(trust_index))

        # -------------------------------------------------------------------
        # Log JSON flatten (OpenSearch)
        # -------------------------------------------------------------------
        log_record = {
            "event": "ai_predict",
            "prompt": prompt,
            "scenario": scenario_tag,
            "answer": answer,
            "quality_score": quality,
            "hallucination_suspected": hallucination_suspected,
            "estimated_cost_eur": estimated_cost,
            "latency_ms": latency_ms,
            # champs d'évaluation à plat
            "mode": mode,
            "coherence": coherence,
            "hallucination": hallucination,
            "risk_flag": risk_flag,
            "risk_reason": risk_reason,
            "ai_act_risk_level": ai_act_risk_level,
            "drift_factor": drift_factor,
            "trust_index": trust_index,
            "error": error,
        }
        logger.info(json.dumps(log_record, ensure_ascii=False))

        # -------------------------------------------------------------------
        # Réponse API (jamais de champs null)
        # -------------------------------------------------------------------
        resp = PredictResponse(
            prompt=prompt,
            scenario=scenario_tag,
            answer=answer,
            quality_score=float(quality),
            hallucination_suspected=bool(hallucination_suspected),
            estimated_cost_eur=float(estimated_cost),
            latency_ms=float(latency_ms),
            mode=mode,
            coherence=float(coherence),
            hallucination=bool(hallucination),
            risk_flag=bool(risk_flag),
            risk_reason=risk_reason,
            ai_act_risk_level=ai_act_risk_level,
            drift_factor=float(drift_factor),
        )

        return JSONResponse(content=json.loads(resp.json()))

