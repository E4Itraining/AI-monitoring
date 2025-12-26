import logging
import os
import random
import time
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# --- Logging setup ---
os.makedirs("/logs", exist_ok=True)
log_path = "/logs/app.log"

logger = logging.getLogger("ai-app")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)
formatter = logging.Formatter(
    '{"@timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
)
fh.setFormatter(formatter)
logger.addHandler(fh)

# --- OpenTelemetry Tracing ---
service_name = os.getenv("OTEL_SERVICE_NAME", "ai-demo-app")

resource = Resource(attributes={"service.name": service_name})

provider = TracerProvider(resource=resource)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(span_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# --- Prometheus Metrics ---
REQUEST_COUNTER = Counter(
    "ai_requests_total", "Total number of AI requests", ["scenario"]
)
ERROR_COUNTER = Counter(
    "ai_request_errors_total", "Total number of AI request errors", ["scenario"]
)
HALLUCINATION_COUNTER = Counter(
    "ai_hallucination_suspected_total",
    "Total number of suspected hallucinations",
    ["scenario"],
)
LATENCY_HIST = Histogram(
    "ai_response_latency_seconds", "AI response latency in seconds", ["scenario"]
)
QUALITY_GAUGE = Gauge(
    "ai_response_quality_score",
    "Quality score of AI response between 0 and 1",
    ["scenario"],
)
COST_COUNTER = Counter(
    "ai_estimated_cost_eur_total",
    "Estimated cost of AI calls in EUR",
    ["scenario"],
)


class PredictRequest(BaseModel):
    prompt: str
    scenario: Optional[str] = "A"  # A: nominal, B: drift, C: stress


class PredictResponse(BaseModel):
    prompt: str
    scenario: str
    answer: str
    quality_score: float
    hallucination_suspected: bool
    latency_ms: float
    estimated_cost_eur: float


app = FastAPI(title="AI Observability Lab - OSMC Edition")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    scenario = (req.scenario or "A").upper()
    if scenario not in ("A", "B", "C"):
        scenario = "A"

    REQUEST_COUNTER.labels(scenario=scenario).inc()

    start = time.time()
    with tracer.start_as_current_span("ai_predict") as span:
        span.set_attribute("ai.scenario", scenario)
        span.set_attribute("ai.prompt_length", len(req.prompt))

        # Simulate processing time depending on scenario
        if scenario == "A":
            time.sleep(random.uniform(0.05, 0.15))
        elif scenario == "B":
            time.sleep(random.uniform(0.1, 0.25))
        else:  # C - stress
            time.sleep(random.uniform(0.2, 0.5))

        # Simple fake "answer"
        answer = f"Demo answer for scenario {scenario}: your prompt was '{req.prompt[:60]}'..."

        # Simulate quality score and hallucination probability
        if scenario == "A":
            quality = random.uniform(0.8, 0.95)
            hallucination = random.random() < 0.05
        elif scenario == "B":
            quality = random.uniform(0.4, 0.8)
            hallucination = random.random() < 0.25
        else:  # C
            quality = random.uniform(0.5, 0.9)
            hallucination = random.random() < 0.15

        # Simulate occasional error for demo
        if scenario != "A" and random.random() < 0.05:
            ERROR_COUNTER.labels(scenario=scenario).inc()
            logger.error(f"AI error in scenario {scenario} for prompt='{req.prompt}'")
            span.set_attribute("ai.error", True)

        if hallucination:
            HALLUCINATION_COUNTER.labels(scenario=scenario).inc()
            span.set_attribute("ai.hallucination_suspected", True)

        # Simple cost estimation: depends on prompt length and scenario
        base_cost = 0.00001 * len(req.prompt)
        multiplier = {"A": 1.0, "B": 1.1, "C": 1.3}[scenario]
        estimated_cost = base_cost * multiplier
        COST_COUNTER.labels(scenario=scenario).inc(estimated_cost)

        elapsed = time.time() - start
        LATENCY_HIST.labels(scenario=scenario).observe(elapsed)
        QUALITY_GAUGE.labels(scenario=scenario).set(quality)

        logger.info(
            f"scenario={scenario} prompt_len={len(req.prompt)} quality={quality:.3f} "
            f"hallucination={hallucination} latency={elapsed:.3f} cost_eur={estimated_cost:.6f}"
        )

        span.set_attribute("ai.quality_score", quality)
        span.set_attribute("ai.estimated_cost_eur", estimated_cost)
        span.set_attribute("ai.latency_ms", elapsed * 1000.0)

    return PredictResponse(
        prompt=req.prompt,
        scenario=scenario,
        answer=answer,
        quality_score=quality,
        hallucination_suspected=hallucination,
        latency_ms=elapsed * 1000.0,
        estimated_cost_eur=estimated_cost,
    )


FastAPIInstrumentor.instrument_app(app)
