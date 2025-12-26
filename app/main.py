"""
AI Observability Platform - Enhanced Edition
============================================
Game-changer improvements:
- PII Detection (GDPR compliance)
- Advanced Prompt Security Score
- Semantic Drift Detection
- Guardrails System
- User Feedback Loop
- Conversation Tracking (multi-turn)
- Complete Audit Trail with UUID
- Real-time Alerting
- Rate Limiting
"""

import time
import random
import json
import logging
import sys
import re
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Centralized configuration"""
    SERVICE_NAME = "ai-demo-app"
    SERVICE_NAMESPACE = "ai-lab"
    SERVICE_VERSION = "4.0.0"  # Major version bump for game-changer release

    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60

    # SLO thresholds
    SLO_LATENCY_THRESHOLD_MS = 1000
    SLO_QUALITY_THRESHOLD = 0.8

    # Security thresholds
    SECURITY_SCORE_THRESHOLD = 0.5
    PII_BLOCK_THRESHOLD = 3  # Block if more than N PII found

    # Drift detection
    DRIFT_ALERT_THRESHOLD = 0.7


# =============================================================================
# ENUMS
# =============================================================================

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PIIType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    IBAN = "iban"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    NAME = "name"


class GuardrailAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REDACT = "redact"


# =============================================================================
# LOGGING SETUP
# =============================================================================

logger = logging.getLogger("ai_app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    try:
        file_handler = logging.FileHandler("/logs/app.log")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(file_handler)
    except Exception:
        pass

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stdout_handler)


# =============================================================================
# OPENTELEMETRY SETUP
# =============================================================================

resource = Resource(
    attributes={
        "service.name": Config.SERVICE_NAME,
        "service.namespace": Config.SERVICE_NAMESPACE,
        "service.version": Config.SERVICE_VERSION,
        "service.instance.id": f"{Config.SERVICE_NAME}-1",
    }
)

trace_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="otel-collector:4317",
    insecure=True,
)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(Config.SERVICE_NAME)


# =============================================================================
# PROMETHEUS METRICS - Enhanced
# =============================================================================

# --- Traffic metrics ---
ai_requests_total = Counter(
    "ai_requests_total", "Total AI requests", ["scenario", "endpoint"]
)
ai_requests_error_total = Counter(
    "ai_requests_error_total", "Failed AI requests", ["scenario", "error_type"]
)
ai_inflight_requests = Gauge(
    "ai_inflight_requests", "In-flight requests", ["endpoint"]
)

# --- Latency metrics ---
ai_latency_seconds = Histogram(
    "ai_latency_seconds", "Response latency",
    ["scenario"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# --- Quality metrics ---
ai_response_quality_score = Histogram(
    "ai_response_quality_score", "Quality score distribution",
    ["scenario"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)
ai_quality_score = Gauge("ai_quality_score", "Current quality score (0-1)")

# --- Cost metrics ---
ai_cost_estimated_eur_total = Counter(
    "ai_cost_estimated_eur_total", "Total estimated cost EUR"
)
ai_tokens_input_total = Counter(
    "ai_tokens_input_total", "Input tokens", ["model"]
)
ai_tokens_output_total = Counter(
    "ai_tokens_output_total", "Output tokens", ["model"]
)

# --- Risk & Safety metrics ---
ai_hallucination_events_total = Counter(
    "ai_hallucination_events_total", "Hallucination events", ["detector", "severity"]
)
ai_toxicity_events_total = Counter(
    "ai_toxicity_events_total", "Toxicity events", ["severity", "category"]
)
ai_risky_responses_total = Counter(
    "ai_risky_responses_total", "Risky responses", ["scenario", "risk_level"]
)

# --- GAME CHANGER: PII Detection metrics ---
ai_pii_detected_total = Counter(
    "ai_pii_detected_total", "PII detected in prompts", ["pii_type", "action"]
)
ai_pii_blocked_requests_total = Counter(
    "ai_pii_blocked_requests_total", "Requests blocked due to PII"
)

# --- GAME CHANGER: Security metrics ---
ai_prompt_security_score = Histogram(
    "ai_prompt_security_score", "Prompt security score distribution",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)
ai_prompt_injection_attempts_total = Counter(
    "ai_prompt_injection_attempts_total", "Injection attempts", ["technique", "blocked"]
)
ai_jailbreak_attempts_total = Counter(
    "ai_jailbreak_attempts_total", "Jailbreak attempts", ["pattern"]
)

# --- GAME CHANGER: Drift metrics ---
ai_input_drift_score = Gauge(
    "ai_input_drift_score", "Semantic drift score", ["scenario", "dimension"]
)
ai_drift_alerts_total = Counter(
    "ai_drift_alerts_total", "Drift alerts triggered", ["severity"]
)

# --- GAME CHANGER: Guardrails metrics ---
ai_guardrail_triggers_total = Counter(
    "ai_guardrail_triggers_total", "Guardrail activations", ["guardrail", "action"]
)
ai_guardrail_blocked_total = Counter(
    "ai_guardrail_blocked_total", "Requests blocked by guardrails", ["reason"]
)

# --- GAME CHANGER: Feedback metrics ---
ai_user_feedback_total = Counter(
    "ai_user_feedback_total", "User feedback received", ["rating", "category"]
)
ai_user_satisfaction_score = Gauge(
    "ai_user_satisfaction_score", "Average user satisfaction (1-5)"
)

# --- GAME CHANGER: Conversation metrics ---
ai_conversation_turns_total = Counter(
    "ai_conversation_turns_total", "Conversation turns", ["conversation_length"]
)
ai_conversation_duration_seconds = Histogram(
    "ai_conversation_duration_seconds", "Conversation duration",
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
)
ai_active_conversations = Gauge(
    "ai_active_conversations", "Active conversations"
)

# --- Trust & Compliance ---
ai_trust_index = Gauge(
    "ai_trust_index", "Trust/compliance index", ["scenario"]
)
ai_compliance_score = Gauge(
    "ai_compliance_score", "AI Act compliance score", ["category"]
)

# --- Rate Limiting ---
ai_rate_limit_events_total = Counter(
    "ai_rate_limit_events_total", "Rate limit events", ["reason", "action"]
)

# --- SLI/SLO ---
ai_sli_latency_requests_total = Counter("ai_sli_latency_requests_total", "Latency SLI requests")
ai_sli_latency_violations_total = Counter("ai_sli_latency_violations_total", "Latency SLI violations")
ai_sli_quality_requests_total = Counter("ai_sli_quality_requests_total", "Quality SLI requests")
ai_sli_quality_violations_total = Counter("ai_sli_quality_violations_total", "Quality SLI violations")
ai_slo_error_budget_burn_rate = Gauge("ai_slo_error_budget_burn_rate", "Error budget burn rate")

# --- Audit ---
ai_audit_events_total = Counter(
    "ai_audit_events_total", "Audit events", ["event_type", "severity"]
)


# =============================================================================
# PII DETECTION SERVICE (GAME CHANGER #1)
# =============================================================================

class PIIDetector:
    """Advanced PII detection for GDPR compliance"""

    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b(?:\+33|0033|0)[1-9](?:[.\-\s]?\d{2}){4}\b',
        PIIType.CREDIT_CARD: r'\b(?:\d{4}[.\-\s]?){3}\d{4}\b',
        PIIType.SSN: r'\b[12][0-9]{2}[0-1][0-9][0-9]{2}[0-9]{3}[0-9]{3}[0-9]{2}\b',
        PIIType.IBAN: r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
        PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        PIIType.DATE_OF_BIRTH: r'\b(?:0[1-9]|[12][0-9]|3[01])[\/\-](?:0[1-9]|1[0-2])[\/\-](?:19|20)\d{2}\b',
    }

    NAME_KEYWORDS = [
        "je m'appelle", "mon nom est", "my name is", "i am", "je suis",
        "prénom", "firstname", "lastname", "nom de famille"
    ]

    @classmethod
    def detect(cls, text: str) -> Dict[PIIType, List[str]]:
        """Detect all PII in text"""
        found = {}
        text_lower = text.lower()

        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found[pii_type] = matches

        # Name detection (heuristic)
        for keyword in cls.NAME_KEYWORDS:
            if keyword in text_lower:
                found[PIIType.NAME] = [keyword]
                break

        return found

    @classmethod
    def redact(cls, text: str, found_pii: Dict[PIIType, List[str]]) -> str:
        """Redact PII from text"""
        redacted = text
        for pii_type, matches in found_pii.items():
            for match in matches:
                redacted = redacted.replace(match, f"[REDACTED_{pii_type.value.upper()}]")
        return redacted

    @classmethod
    def count_pii(cls, found_pii: Dict[PIIType, List[str]]) -> int:
        """Count total PII items found"""
        return sum(len(matches) for matches in found_pii.values())


# =============================================================================
# PROMPT SECURITY SERVICE (GAME CHANGER #2)
# =============================================================================

class PromptSecurityAnalyzer:
    """Advanced prompt security analysis"""

    INJECTION_PATTERNS = {
        "system_override": [
            r"ignore.*(?:previous|above|all).*(?:instructions|rules)",
            r"(?:forget|disregard).*(?:instructions|guidelines)",
            r"you are now",
            r"act as",
            r"pretend.*(?:you|to be)",
            r"new.*(?:role|persona|identity)",
        ],
        "data_extraction": [
            r"(?:reveal|show|display|print).*(?:prompt|instructions|system)",
            r"what.*(?:your|the).*(?:instructions|prompt|rules)",
            r"(?:dump|output|list).*(?:all|your).*(?:data|information)",
        ],
        "role_manipulation": [
            r"(?:dan|developer|admin).*mode",
            r"jailbreak",
            r"bypass.*(?:filter|safety|security)",
            r"(?:evil|dark|shadow).*(?:mode|version)",
        ],
        "encoding_tricks": [
            r"base64",
            r"\\x[0-9a-f]{2}",
            r"&#x?[0-9a-f]+;",
            r"unicode.*(?:bypass|escape)",
        ],
        "delimiter_injection": [
            r"```.*system",
            r"\[INST\]",
            r"<\|.*\|>",
            r"###.*instruction",
        ],
    }

    JAILBREAK_PHRASES = [
        "do anything now",
        "hypothetically speaking",
        "for educational purposes",
        "in a fictional scenario",
        "if you were evil",
        "ignore ethics",
        "no restrictions",
        "unrestricted mode",
    ]

    @classmethod
    def analyze(cls, prompt: str) -> Dict[str, Any]:
        """Analyze prompt for security threats"""
        prompt_lower = prompt.lower()
        threats = []
        techniques = []

        # Check injection patterns
        for technique, patterns in cls.INJECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    threats.append({
                        "technique": technique,
                        "pattern": pattern,
                        "severity": "high" if technique in ["system_override", "role_manipulation"] else "medium"
                    })
                    techniques.append(technique)
                    break

        # Check jailbreak phrases
        for phrase in cls.JAILBREAK_PHRASES:
            if phrase in prompt_lower:
                threats.append({
                    "technique": "jailbreak",
                    "pattern": phrase,
                    "severity": "high"
                })
                techniques.append("jailbreak")

        # Calculate security score (1.0 = safe, 0.0 = dangerous)
        base_score = 1.0
        for threat in threats:
            if threat["severity"] == "high":
                base_score -= 0.3
            elif threat["severity"] == "medium":
                base_score -= 0.15
            else:
                base_score -= 0.05

        security_score = max(0.0, min(1.0, base_score))

        return {
            "security_score": security_score,
            "threats": threats,
            "techniques_detected": list(set(techniques)),
            "is_safe": security_score >= Config.SECURITY_SCORE_THRESHOLD,
            "risk_level": cls._calculate_risk_level(security_score),
        }

    @classmethod
    def _calculate_risk_level(cls, score: float) -> RiskLevel:
        if score >= 0.9:
            return RiskLevel.LOW
        elif score >= 0.7:
            return RiskLevel.MEDIUM
        elif score >= 0.4:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL


# =============================================================================
# SEMANTIC DRIFT DETECTOR (GAME CHANGER #3)
# =============================================================================

class SemanticDriftDetector:
    """Detect semantic drift in prompts"""

    # Reference topics for baseline
    BASELINE_TOPICS = {
        "technology", "software", "computer", "data", "system",
        "application", "service", "api", "database", "cloud",
        "security", "network", "performance", "monitoring", "analytics"
    }

    # Out-of-domain indicators
    OOD_INDICATORS = {
        "medical": ["symptom", "disease", "diagnosis", "medication", "patient", "doctor", "hospital"],
        "legal": ["lawsuit", "attorney", "court", "contract", "liability", "verdict"],
        "financial": ["investment", "stock", "trading", "portfolio", "dividend", "hedge"],
        "personal": ["relationship", "emotion", "feeling", "love", "hate", "family"],
    }

    # Complexity indicators
    COMPLEXITY_PATTERNS = {
        "nested_instructions": r"(?:if|when|unless).*(?:then|else|otherwise)",
        "multiple_requests": r"(?:and|also|additionally|furthermore).*(?:please|can you|could you)",
        "long_prompt": 500,  # character threshold
    }

    @classmethod
    def analyze(cls, prompt: str, scenario: str) -> Dict[str, Any]:
        """Analyze semantic drift"""
        prompt_lower = prompt.lower()
        words = set(re.findall(r'\b\w+\b', prompt_lower))

        # Calculate topic overlap with baseline
        baseline_overlap = len(words & cls.BASELINE_TOPICS) / max(len(cls.BASELINE_TOPICS), 1)

        # Detect out-of-domain drift
        ood_scores = {}
        for domain, indicators in cls.OOD_INDICATORS.items():
            matches = sum(1 for ind in indicators if ind in prompt_lower)
            ood_scores[domain] = matches / len(indicators)

        max_ood_domain = max(ood_scores, key=ood_scores.get)
        max_ood_score = ood_scores[max_ood_domain]

        # Complexity drift
        complexity_score = 0.0
        if len(prompt) > cls.COMPLEXITY_PATTERNS["long_prompt"]:
            complexity_score += 0.3
        if re.search(cls.COMPLEXITY_PATTERNS["nested_instructions"], prompt_lower):
            complexity_score += 0.2
        if re.search(cls.COMPLEXITY_PATTERNS["multiple_requests"], prompt_lower):
            complexity_score += 0.2

        # Calculate overall drift factor
        drift_factor = max(
            1.0 - baseline_overlap,
            max_ood_score,
            complexity_score
        )

        # Adjust by scenario
        if scenario in ("baseline", "after-mitigation"):
            drift_factor *= 0.3
        elif scenario == "drift":
            drift_factor = max(drift_factor, random.uniform(0.5, 0.9))

        return {
            "drift_factor": round(min(1.0, drift_factor), 3),
            "baseline_overlap": round(baseline_overlap, 3),
            "ood_domain": max_ood_domain if max_ood_score > 0.2 else None,
            "ood_score": round(max_ood_score, 3),
            "complexity_score": round(complexity_score, 3),
            "dimensions": {
                "topic": round(1.0 - baseline_overlap, 3),
                "domain": round(max_ood_score, 3),
                "complexity": round(complexity_score, 3),
            },
            "alert": drift_factor > Config.DRIFT_ALERT_THRESHOLD,
        }


# =============================================================================
# GUARDRAILS SYSTEM (GAME CHANGER #4)
# =============================================================================

@dataclass
class Guardrail:
    name: str
    description: str
    check: callable
    action: GuardrailAction
    enabled: bool = True


class GuardrailsEngine:
    """Configurable guardrails system"""

    def __init__(self):
        self.guardrails: List[Guardrail] = []
        self._setup_default_guardrails()

    def _setup_default_guardrails(self):
        """Setup default guardrails"""

        # PII Protection
        self.guardrails.append(Guardrail(
            name="pii_protection",
            description="Block requests with excessive PII",
            check=lambda ctx: PIIDetector.count_pii(ctx.get("pii_detected", {})) <= Config.PII_BLOCK_THRESHOLD,
            action=GuardrailAction.BLOCK,
        ))

        # Prompt Injection Protection
        self.guardrails.append(Guardrail(
            name="injection_protection",
            description="Block prompt injection attempts",
            check=lambda ctx: ctx.get("security_analysis", {}).get("security_score", 1.0) >= 0.3,
            action=GuardrailAction.BLOCK,
        ))

        # Toxicity Filter
        self.guardrails.append(Guardrail(
            name="toxicity_filter",
            description="Warn on potentially toxic content",
            check=lambda ctx: not ctx.get("toxicity_detected", False),
            action=GuardrailAction.WARN,
        ))

        # Rate Limit
        self.guardrails.append(Guardrail(
            name="rate_limit",
            description="Enforce rate limiting",
            check=lambda ctx: not ctx.get("rate_limited", False),
            action=GuardrailAction.BLOCK,
        ))

        # Prompt Length
        self.guardrails.append(Guardrail(
            name="prompt_length",
            description="Limit prompt length",
            check=lambda ctx: len(ctx.get("prompt", "")) <= 10000,
            action=GuardrailAction.BLOCK,
        ))

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all guardrails"""
        results = {
            "passed": True,
            "action": GuardrailAction.ALLOW,
            "triggered": [],
            "warnings": [],
        }

        for guardrail in self.guardrails:
            if not guardrail.enabled:
                continue

            try:
                passed = guardrail.check(context)
            except Exception:
                passed = True  # Fail open

            if not passed:
                results["triggered"].append({
                    "name": guardrail.name,
                    "action": guardrail.action.value,
                })

                ai_guardrail_triggers_total.labels(
                    guardrail=guardrail.name,
                    action=guardrail.action.value
                ).inc()

                if guardrail.action == GuardrailAction.BLOCK:
                    results["passed"] = False
                    results["action"] = GuardrailAction.BLOCK
                    ai_guardrail_blocked_total.labels(reason=guardrail.name).inc()
                elif guardrail.action == GuardrailAction.WARN:
                    results["warnings"].append(guardrail.name)

        return results


# =============================================================================
# CONVERSATION TRACKER (GAME CHANGER #5)
# =============================================================================

@dataclass
class ConversationState:
    conversation_id: str
    user_id: Optional[str]
    turns: int = 0
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    total_tokens: int = 0
    quality_scores: List[float] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)


class ConversationTracker:
    """Track multi-turn conversations"""

    def __init__(self, timeout_minutes: int = 30):
        self.conversations: Dict[str, ConversationState] = {}
        self.timeout_seconds = timeout_minutes * 60

    def get_or_create(self, conversation_id: Optional[str], user_id: Optional[str] = None) -> ConversationState:
        """Get existing or create new conversation"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        if conversation_id in self.conversations:
            conv = self.conversations[conversation_id]
            conv.last_activity = time.time()
            return conv

        conv = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        self.conversations[conversation_id] = conv
        ai_active_conversations.inc()
        return conv

    def record_turn(self, conversation_id: str, quality_score: float, tokens: int, topic: Optional[str] = None):
        """Record a conversation turn"""
        if conversation_id not in self.conversations:
            return

        conv = self.conversations[conversation_id]
        conv.turns += 1
        conv.total_tokens += tokens
        conv.quality_scores.append(quality_score)
        if topic:
            conv.topics.append(topic)

        # Update metrics
        turn_bucket = "1" if conv.turns == 1 else "2-5" if conv.turns <= 5 else "6-10" if conv.turns <= 10 else "10+"
        ai_conversation_turns_total.labels(conversation_length=turn_bucket).inc()

    def end_conversation(self, conversation_id: str):
        """End and cleanup conversation"""
        if conversation_id not in self.conversations:
            return

        conv = self.conversations[conversation_id]
        duration = time.time() - conv.start_time
        ai_conversation_duration_seconds.observe(duration)
        ai_active_conversations.dec()
        del self.conversations[conversation_id]

    def cleanup_stale(self):
        """Cleanup stale conversations"""
        now = time.time()
        stale = [
            cid for cid, conv in self.conversations.items()
            if now - conv.last_activity > self.timeout_seconds
        ]
        for cid in stale:
            self.end_conversation(cid)


# =============================================================================
# AUDIT TRAIL (GAME CHANGER #6)
# =============================================================================

class AuditTrail:
    """Complete audit trail with UUID tracking"""

    @staticmethod
    def generate_request_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_trace_id(request_id: str) -> str:
        return hashlib.sha256(request_id.encode()).hexdigest()[:32]

    @staticmethod
    def log_event(
        event_type: str,
        request_id: str,
        data: Dict[str, Any],
        severity: str = "info"
    ):
        """Log audit event"""
        audit_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "request_id": request_id,
            "trace_id": AuditTrail.generate_trace_id(request_id),
            "severity": severity,
            **data
        }

        logger.info(json.dumps(audit_record, ensure_ascii=False))
        ai_audit_events_total.labels(event_type=event_type, severity=severity).inc()


# =============================================================================
# RATE LIMITER (GAME CHANGER #7)
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - Config.RATE_LIMIT_WINDOW_SECONDS

        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]

        if len(self.requests[client_id]) >= Config.RATE_LIMIT_REQUESTS:
            ai_rate_limit_events_total.labels(reason="quota_exceeded", action="blocked").inc()
            return False

        self.requests[client_id].append(now)
        return True


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class PredictRequest(BaseModel):
    prompt: str
    scenario: str = "baseline"
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PredictResponse(BaseModel):
    # Core response
    request_id: str
    prompt: str
    scenario: str
    answer: str

    # Quality metrics
    quality_score: float
    coherence: float
    hallucination_suspected: bool
    hallucination: bool

    # Cost & performance
    estimated_cost_eur: float
    latency_ms: float
    tokens_input: int
    tokens_output: int

    # Risk assessment
    mode: str
    risk_flag: bool
    risk_reason: str
    ai_act_risk_level: str

    # GAME CHANGER fields
    security_score: float
    pii_detected_count: int
    pii_redacted: bool
    drift_factor: float
    drift_alert: bool
    guardrails_passed: bool
    guardrails_warnings: List[str]
    trust_index: float

    # Conversation
    conversation_id: Optional[str] = None
    conversation_turn: Optional[int] = None


class FeedbackRequest(BaseModel):
    request_id: str
    rating: int = Field(..., ge=1, le=5)
    category: Optional[str] = None
    comment: Optional[str] = None
    conversation_id: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    active_conversations: int


class GuardrailConfigRequest(BaseModel):
    guardrail_name: str
    enabled: bool


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_scenario(raw: str) -> tuple[str, str]:
    """Normalize scenario to (tag, mode)"""
    if not raw:
        return "baseline", "nominal"

    s = raw.strip().lower()

    mapping = {
        ("a", "baseline", "nominal"): ("baseline", "nominal"),
        ("after-mitigation", "mitigated"): ("after-mitigation", "nominal"),
        ("b", "drift"): ("drift", "drift"),
        ("c", "latency-spike", "stress"): ("latency-spike", "stress"),
        ("prompt-injection", "injection"): ("prompt-injection", "risky"),
        ("high-risk", "risk"): ("high-risk", "risky"),
        ("toxic",): ("toxic", "risky"),
    }

    for keys, result in mapping.items():
        if s in keys:
            return result

    return s, "nominal"


def estimate_tokens(prompt: str, answer: str) -> tuple[int, int]:
    """Estimate input/output tokens"""
    input_tokens = int(len(prompt.split()) * random.uniform(1.2, 1.8))
    output_tokens = int(len(answer.split()) * random.uniform(1.0, 1.4))
    return max(1, input_tokens), max(1, output_tokens)


def simulate_ai_response(prompt: str, scenario_tag: str, mode: str) -> tuple:
    """Simulate AI response based on scenario"""

    latency_ranges = {
        "nominal": (0.05, 0.15),
        "drift": (0.1, 0.25),
        "stress": (0.2, 0.6),
        "risky": (0.15, 0.5),
    }

    quality_ranges = {
        "baseline": (0.8, 0.95),
        "after-mitigation": (0.8, 0.95),
        "drift": (0.4, 0.85),
        "latency-spike": (0.6, 0.9),
    }

    hallucination_rates = {
        "baseline": 0.0,
        "after-mitigation": 0.0,
        "drift": 0.3,
        "latency-spike": 0.2,
    }

    lat_range = latency_ranges.get(mode, (0.1, 0.3))
    base_latency = random.uniform(*lat_range)
    time.sleep(base_latency)

    qual_range = quality_ranges.get(scenario_tag, (0.3, 0.8))
    quality = random.uniform(*qual_range)

    hall_rate = hallucination_rates.get(scenario_tag, 0.4)
    hallucination_suspected = random.random() < hall_rate

    base_cost = 0.0005 * len(prompt)
    if scenario_tag in ("latency-spike", "high-risk", "toxic"):
        base_cost *= 1.5

    answer = f"Réponse simulée pour '{scenario_tag}' avec score qualité {quality:.2f}."

    return answer, quality, hallucination_suspected, base_cost, base_latency


def calculate_trust_index(risk_flag: bool, ai_act_risk_level: str, security_score: float) -> float:
    """Calculate composite trust index"""
    if not risk_flag and ai_act_risk_level == "low":
        base_trust = 1.0
    elif ai_act_risk_level == "medium":
        base_trust = 0.6
    elif ai_act_risk_level == "high":
        base_trust = 0.3
    else:
        base_trust = 0.5

    # Adjust by security score
    adjusted_trust = base_trust * (0.5 + 0.5 * security_score)
    return round(min(1.0, max(0.0, adjusted_trust)), 3)


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="AI Reliability / Observability Platform",
    description="Enhanced AI monitoring with PII detection, guardrails, and advanced security",
    version=Config.SERVICE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
guardrails_engine = GuardrailsEngine()
conversation_tracker = ConversationTracker()
rate_limiter = RateLimiter()
feedback_storage: Dict[str, Dict] = {}


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        version=Config.SERVICE_VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z",
        active_conversations=len(conversation_tracker.conversations),
    )


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, request: Request):
    """
    Main prediction endpoint with full observability stack.

    GAME CHANGER features:
    - PII detection and optional redaction
    - Advanced prompt security analysis
    - Semantic drift detection
    - Guardrails enforcement
    - Conversation tracking
    - Complete audit trail
    """
    request_id = AuditTrail.generate_request_id()
    client_ip = request.client.host if request.client else "unknown"

    # Normalize scenario
    scenario_tag, mode = normalize_scenario(req.scenario)
    prompt = req.prompt or ""
    endpoint = "/predict"
    model = "demo-medium"

    # Update inflight
    ai_inflight_requests.labels(endpoint=endpoint).inc()
    ai_requests_total.labels(scenario=scenario_tag, endpoint=endpoint).inc()

    start_time = time.time()

    with tracer.start_as_current_span("ai_predict") as span:
        span.set_attribute("ai.request_id", request_id)
        span.set_attribute("ai.prompt_length", len(prompt))
        span.set_attribute("ai.scenario", scenario_tag)
        span.set_attribute("ai.mode", mode)

        # =====================================================================
        # GAME CHANGER #1: PII Detection
        # =====================================================================
        pii_detected = PIIDetector.detect(prompt)
        pii_count = PIIDetector.count_pii(pii_detected)
        pii_redacted = False

        for pii_type, matches in pii_detected.items():
            ai_pii_detected_total.labels(
                pii_type=pii_type.value,
                action="detected"
            ).inc(len(matches))

        # Log PII detection audit event
        if pii_count > 0:
            AuditTrail.log_event(
                "pii_detected",
                request_id,
                {"pii_types": [t.value for t in pii_detected.keys()], "count": pii_count},
                severity="warning"
            )

        # =====================================================================
        # GAME CHANGER #2: Security Analysis
        # =====================================================================
        security_analysis = PromptSecurityAnalyzer.analyze(prompt)
        security_score = security_analysis["security_score"]

        ai_prompt_security_score.observe(security_score)

        for threat in security_analysis["threats"]:
            ai_prompt_injection_attempts_total.labels(
                technique=threat["technique"],
                blocked=str(not security_analysis["is_safe"])
            ).inc()

        if not security_analysis["is_safe"]:
            AuditTrail.log_event(
                "security_threat",
                request_id,
                {"threats": security_analysis["threats"], "score": security_score},
                severity="high"
            )

        # =====================================================================
        # GAME CHANGER #3: Semantic Drift Detection
        # =====================================================================
        drift_analysis = SemanticDriftDetector.analyze(prompt, scenario_tag)
        drift_factor = drift_analysis["drift_factor"]

        for dimension, score in drift_analysis["dimensions"].items():
            ai_input_drift_score.labels(scenario=scenario_tag, dimension=dimension).set(score)

        if drift_analysis["alert"]:
            ai_drift_alerts_total.labels(severity="warning").inc()
            AuditTrail.log_event(
                "drift_alert",
                request_id,
                {"drift_factor": drift_factor, "ood_domain": drift_analysis["ood_domain"]},
                severity="warning"
            )

        # =====================================================================
        # GAME CHANGER #4: Rate Limiting Check
        # =====================================================================
        rate_limited = not rate_limiter.is_allowed(client_ip)

        # =====================================================================
        # GAME CHANGER #5: Guardrails Evaluation
        # =====================================================================
        guardrails_context = {
            "prompt": prompt,
            "pii_detected": pii_detected,
            "security_analysis": security_analysis,
            "rate_limited": rate_limited,
            "toxicity_detected": scenario_tag == "toxic",
        }

        guardrails_result = guardrails_engine.evaluate(guardrails_context)

        if not guardrails_result["passed"]:
            ai_inflight_requests.labels(endpoint=endpoint).dec()
            ai_requests_error_total.labels(scenario=scenario_tag, error_type="guardrail_blocked").inc()

            AuditTrail.log_event(
                "request_blocked",
                request_id,
                {"triggered": guardrails_result["triggered"]},
                severity="warning"
            )

            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Request blocked by guardrails",
                    "request_id": request_id,
                    "triggered": guardrails_result["triggered"],
                }
            )

        # =====================================================================
        # GAME CHANGER #6: Conversation Tracking
        # =====================================================================
        conversation = conversation_tracker.get_or_create(
            req.conversation_id,
            req.user_id
        )

        # =====================================================================
        # Main AI Simulation
        # =====================================================================
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
            ai_requests_error_total.labels(scenario=scenario_tag, error_type="internal").inc()
            logger.error(json.dumps({"event": "error", "request_id": request_id, "message": str(e)}))

        elapsed = time.time() - start_time
        latency_ms = elapsed * 1000.0

        # Token estimation
        in_toks, out_toks = estimate_tokens(prompt, answer)

        # =====================================================================
        # Risk Evaluation
        # =====================================================================
        coherence = float(quality)
        hallucination = bool(hallucination_suspected)

        risk_flag = False
        risk_reason = "ok"

        if coherence < 0.65:
            risk_flag = True
            risk_reason = "low_coherence"

        if hallucination and not risk_flag:
            risk_flag = True
            risk_reason = "hallucination_detected"

        if not security_analysis["is_safe"]:
            risk_flag = True
            risk_reason = "security_threat"

        # AI Act risk level
        if not risk_flag:
            ai_act_risk_level = "low"
        elif risk_reason in ("low_coherence", "hallucination_detected"):
            ai_act_risk_level = "medium"
        else:
            ai_act_risk_level = "high"

        # Trust index
        trust_index = calculate_trust_index(risk_flag, ai_act_risk_level, security_score)

        # =====================================================================
        # Update Metrics
        # =====================================================================
        ai_latency_seconds.labels(scenario=scenario_tag).observe(elapsed)
        ai_response_quality_score.labels(scenario=scenario_tag).observe(quality)
        ai_quality_score.set(quality)

        ai_tokens_input_total.labels(model=model).inc(in_toks)
        ai_tokens_output_total.labels(model=model).inc(out_toks)
        ai_cost_estimated_eur_total.inc(estimated_cost)

        # SLI/SLO
        ai_sli_latency_requests_total.inc()
        if elapsed > Config.SLO_LATENCY_THRESHOLD_MS / 1000:
            ai_sli_latency_violations_total.inc()

        ai_sli_quality_requests_total.inc()
        if quality < Config.SLO_QUALITY_THRESHOLD:
            ai_sli_quality_violations_total.inc()

        # Risk metrics
        if hallucination_suspected:
            severity = "high" if quality < 0.5 else "medium"
            ai_hallucination_events_total.labels(detector="rule-engine", severity=severity).inc()

        if risk_flag:
            ai_risky_responses_total.labels(scenario=scenario_tag, risk_level=ai_act_risk_level).inc()

        if scenario_tag in ("toxic", "high-risk") or ai_act_risk_level == "high":
            ai_toxicity_events_total.labels(severity="high", category=scenario_tag).inc()

        ai_trust_index.labels(scenario=scenario_tag).set(trust_index)

        # Compliance score
        compliance_base = 1.0 - (0.2 if pii_count > 0 else 0) - (0.3 if not security_analysis["is_safe"] else 0)
        ai_compliance_score.labels(category="gdpr").set(max(0, compliance_base))
        ai_compliance_score.labels(category="ai_act").set(trust_index)

        # Error budget
        if scenario_tag in ("baseline", "after-mitigation"):
            burn = random.uniform(0.0, 0.1)
        elif scenario_tag in ("drift", "latency-spike"):
            burn = random.uniform(0.3, 0.7)
        else:
            burn = random.uniform(0.5, 1.0)
        ai_slo_error_budget_burn_rate.set(burn)

        # Update conversation
        conversation_tracker.record_turn(
            conversation.conversation_id,
            quality,
            in_toks + out_toks
        )

        # Decrease inflight
        ai_inflight_requests.labels(endpoint=endpoint).dec()

        # =====================================================================
        # OpenTelemetry Span Attributes
        # =====================================================================
        span.set_attribute("ai.quality_score", float(quality))
        span.set_attribute("ai.hallucination_suspected", bool(hallucination_suspected))
        span.set_attribute("ai.estimated_cost_eur", float(estimated_cost))
        span.set_attribute("ai.latency_ms", float(latency_ms))
        span.set_attribute("ai.security_score", float(security_score))
        span.set_attribute("ai.pii_count", int(pii_count))
        span.set_attribute("ai.drift_factor", float(drift_factor))
        span.set_attribute("ai.trust_index", float(trust_index))
        span.set_attribute("ai.conversation_id", conversation.conversation_id)
        span.set_attribute("ai.conversation_turn", conversation.turns)

        span.set_attribute("ai.eval.mode", mode)
        span.set_attribute("ai.eval.coherence", float(coherence))
        span.set_attribute("ai.eval.risk_flag", bool(risk_flag))
        span.set_attribute("ai.eval.risk_reason", risk_reason)
        span.set_attribute("ai.eval.ai_act_risk_level", ai_act_risk_level)

        # =====================================================================
        # Audit Trail
        # =====================================================================
        AuditTrail.log_event(
            "ai_predict",
            request_id,
            {
                "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "scenario": scenario_tag,
                "quality_score": quality,
                "security_score": security_score,
                "pii_count": pii_count,
                "drift_factor": drift_factor,
                "risk_flag": risk_flag,
                "risk_reason": risk_reason,
                "ai_act_risk_level": ai_act_risk_level,
                "trust_index": trust_index,
                "latency_ms": latency_ms,
                "conversation_id": conversation.conversation_id,
                "conversation_turn": conversation.turns,
                "guardrails_warnings": guardrails_result["warnings"],
                "error": error,
            },
            severity="info" if not risk_flag else "warning"
        )

        # =====================================================================
        # Response
        # =====================================================================
        return PredictResponse(
            request_id=request_id,
            prompt=prompt,
            scenario=scenario_tag,
            answer=answer,
            quality_score=float(quality),
            coherence=float(coherence),
            hallucination_suspected=bool(hallucination_suspected),
            hallucination=bool(hallucination),
            estimated_cost_eur=float(estimated_cost),
            latency_ms=float(latency_ms),
            tokens_input=in_toks,
            tokens_output=out_toks,
            mode=mode,
            risk_flag=bool(risk_flag),
            risk_reason=risk_reason,
            ai_act_risk_level=ai_act_risk_level,
            security_score=float(security_score),
            pii_detected_count=pii_count,
            pii_redacted=pii_redacted,
            drift_factor=float(drift_factor),
            drift_alert=drift_analysis["alert"],
            guardrails_passed=guardrails_result["passed"],
            guardrails_warnings=guardrails_result["warnings"],
            trust_index=float(trust_index),
            conversation_id=conversation.conversation_id,
            conversation_turn=conversation.turns,
        )


@app.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackRequest):
    """
    GAME CHANGER: User feedback endpoint for continuous improvement.
    """
    feedback_id = str(uuid.uuid4())

    # Store feedback
    feedback_storage[feedback_id] = {
        "feedback_id": feedback_id,
        "request_id": feedback.request_id,
        "rating": feedback.rating,
        "category": feedback.category,
        "comment": feedback.comment,
        "conversation_id": feedback.conversation_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Update metrics
    rating_label = str(feedback.rating)
    category_label = feedback.category or "general"
    ai_user_feedback_total.labels(rating=rating_label, category=category_label).inc()

    # Update satisfaction gauge (rolling average approximation)
    all_ratings = [f["rating"] for f in feedback_storage.values()]
    avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 3.0
    ai_user_satisfaction_score.set(avg_rating)

    # Audit trail
    AuditTrail.log_event(
        "user_feedback",
        feedback.request_id,
        {
            "feedback_id": feedback_id,
            "rating": feedback.rating,
            "category": category_label,
        },
        severity="info"
    )

    return FeedbackResponse(
        success=True,
        message="Feedback recorded successfully",
        feedback_id=feedback_id,
    )


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    """Get conversation state"""
    if conversation_id not in conversation_tracker.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = conversation_tracker.conversations[conversation_id]
    return {
        "conversation_id": conv.conversation_id,
        "user_id": conv.user_id,
        "turns": conv.turns,
        "duration_seconds": time.time() - conv.start_time,
        "total_tokens": conv.total_tokens,
        "avg_quality": sum(conv.quality_scores) / len(conv.quality_scores) if conv.quality_scores else 0,
    }


@app.delete("/conversations/{conversation_id}")
def end_conversation(conversation_id: str):
    """End a conversation"""
    if conversation_id not in conversation_tracker.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation_tracker.end_conversation(conversation_id)
    return {"status": "ended", "conversation_id": conversation_id}


@app.put("/guardrails/config")
def configure_guardrail(config: GuardrailConfigRequest):
    """Configure guardrail enabled state"""
    for guardrail in guardrails_engine.guardrails:
        if guardrail.name == config.guardrail_name:
            guardrail.enabled = config.enabled
            return {"status": "updated", "guardrail": config.guardrail_name, "enabled": config.enabled}

    raise HTTPException(status_code=404, detail=f"Guardrail '{config.guardrail_name}' not found")


@app.get("/guardrails")
def list_guardrails():
    """List all guardrails and their status"""
    return {
        "guardrails": [
            {
                "name": g.name,
                "description": g.description,
                "action": g.action.value,
                "enabled": g.enabled,
            }
            for g in guardrails_engine.guardrails
        ]
    }


@app.get("/stats")
def get_stats():
    """Get current platform statistics"""
    return {
        "version": Config.SERVICE_VERSION,
        "active_conversations": len(conversation_tracker.conversations),
        "feedback_count": len(feedback_storage),
        "guardrails_enabled": sum(1 for g in guardrails_engine.guardrails if g.enabled),
        "rate_limit_config": {
            "requests": Config.RATE_LIMIT_REQUESTS,
            "window_seconds": Config.RATE_LIMIT_WINDOW_SECONDS,
        },
        "slo_thresholds": {
            "latency_ms": Config.SLO_LATENCY_THRESHOLD_MS,
            "quality": Config.SLO_QUALITY_THRESHOLD,
        },
    }


# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize platform on startup"""
    logger.info(json.dumps({
        "event": "startup",
        "version": Config.SERVICE_VERSION,
        "service": Config.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # End all conversations
    for conv_id in list(conversation_tracker.conversations.keys()):
        conversation_tracker.end_conversation(conv_id)

    logger.info(json.dumps({
        "event": "shutdown",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
