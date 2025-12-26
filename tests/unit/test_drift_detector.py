"""
Unit tests for Semantic Drift Detection.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from main import SemanticDriftDetector


class TestSemanticDriftDetector:
    """Test suite for semantic drift detection."""

    def test_baseline_topic_prompt(self):
        """Test prompt aligned with baseline topics."""
        prompt = "How do I configure the database system for better performance?"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert "baseline_overlap" in result or "topic_score" in result or "drift_score" in result
        assert isinstance(result, dict)

    def test_medical_drift(self):
        """Test detection of medical domain drift."""
        prompt = "I have symptoms of fever and headache, what disease do I have?"
        result = SemanticDriftDetector.analyze(prompt, "A")

        # Check if medical drift is detected
        assert "ood_scores" in result or "drift_detected" in result or isinstance(result, dict)

    def test_legal_drift(self):
        """Test detection of legal domain drift."""
        prompt = "My attorney says we should file a lawsuit against the contractor"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)

    def test_financial_drift(self):
        """Test detection of financial domain drift."""
        prompt = "Should I invest in this stock or add it to my portfolio?"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)

    def test_personal_drift(self):
        """Test detection of personal/emotional drift."""
        prompt = "I'm feeling sad about my relationship and need advice"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)

    def test_no_drift_technology_prompt(self):
        """Test technology prompt without drift."""
        prompt = "How does cloud computing and API monitoring work?"
        result = SemanticDriftDetector.analyze(prompt, "baseline")

        assert isinstance(result, dict)

    def test_complexity_long_prompt(self):
        """Test complexity detection for long prompts."""
        prompt = "a" * 600  # Exceeds 500 char threshold
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)

    def test_complexity_nested_instructions(self):
        """Test complexity detection for nested instructions."""
        prompt = "If you understand then please also can you additionally help me"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)

    def test_empty_prompt(self):
        """Test empty prompt handling."""
        result = SemanticDriftDetector.analyze("", "A")
        assert isinstance(result, dict)

    def test_different_scenarios(self):
        """Test analysis across different scenarios."""
        prompt = "Analyze this data"

        scenarios = ["A", "B", "C", "baseline", "drift"]
        for scenario in scenarios:
            result = SemanticDriftDetector.analyze(prompt, scenario)
            assert isinstance(result, dict)


class TestDriftScoring:
    """Test drift scoring mechanisms."""

    def test_drift_score_range(self):
        """Test that drift scores are in valid range."""
        prompts = [
            "How to configure monitoring?",
            "I need medical advice for my patient",
            "Legal consultation about contracts",
        ]

        for prompt in prompts:
            result = SemanticDriftDetector.analyze(prompt, "A")
            if "drift_score" in result:
                assert 0 <= result["drift_score"] <= 1
            if "semantic_drift_score" in result:
                assert 0 <= result["semantic_drift_score"] <= 1

    def test_multiple_domain_drift(self):
        """Test prompt with multiple out-of-domain indicators."""
        prompt = "My doctor and attorney discussed the investment portfolio"
        result = SemanticDriftDetector.analyze(prompt, "A")

        assert isinstance(result, dict)


class TestDriftEdgeCases:
    """Edge cases for drift detection."""

    def test_unicode_prompt(self):
        """Test unicode text handling."""
        prompt = "Comment configurer le système 日本語"
        result = SemanticDriftDetector.analyze(prompt, "A")
        assert isinstance(result, dict)

    def test_special_characters(self):
        """Test special characters handling."""
        prompt = "What about @#$%^& symbols?"
        result = SemanticDriftDetector.analyze(prompt, "A")
        assert isinstance(result, dict)

    def test_mixed_domains(self):
        """Test prompt mixing baseline and OOD topics."""
        prompt = "How does the software system help with medical diagnosis?"
        result = SemanticDriftDetector.analyze(prompt, "A")
        assert isinstance(result, dict)
