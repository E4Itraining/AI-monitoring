"""
Unit tests for PII Detection functionality.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from main import PIIDetector, PIIType


class TestPIIDetector:
    """Test suite for PII detection."""

    def test_detect_email(self):
        """Test email detection."""
        text = "Contact me at john.doe@example.com for more info"
        result = PIIDetector.detect(text)

        assert PIIType.EMAIL in result
        assert "john.doe@example.com" in result[PIIType.EMAIL]

    def test_detect_phone_french(self):
        """Test French phone number detection."""
        text = "Mon numéro est 06 12 34 56 78"
        result = PIIDetector.detect(text)

        assert PIIType.PHONE in result

    def test_detect_phone_international(self):
        """Test international phone format."""
        text = "Call me at +33 6 12 34 56 78"
        result = PIIDetector.detect(text)

        assert PIIType.PHONE in result

    def test_detect_credit_card(self):
        """Test credit card number detection."""
        text = "My card number is 4532-1234-5678-9012"
        result = PIIDetector.detect(text)

        assert PIIType.CREDIT_CARD in result

    def test_detect_iban(self):
        """Test IBAN detection."""
        text = "Transfer to FR7630006000011234567890189"
        result = PIIDetector.detect(text)

        assert PIIType.IBAN in result

    def test_detect_ip_address(self):
        """Test IP address detection."""
        text = "Server is at 192.168.1.100"
        result = PIIDetector.detect(text)

        assert PIIType.IP_ADDRESS in result

    def test_detect_date_of_birth(self):
        """Test date of birth detection."""
        text = "Born on 15/03/1990"
        result = PIIDetector.detect(text)

        assert PIIType.DATE_OF_BIRTH in result

    def test_detect_name_french(self):
        """Test French name detection."""
        text = "Je m'appelle Jean Dupont"
        result = PIIDetector.detect(text)

        assert PIIType.NAME in result

    def test_detect_name_english(self):
        """Test English name detection."""
        text = "My name is John Smith"
        result = PIIDetector.detect(text)

        assert PIIType.NAME in result

    def test_detect_multiple_pii(self):
        """Test detection of multiple PII types."""
        text = "Contact john@test.com or call 06.12.34.56.78"
        result = PIIDetector.detect(text)

        assert PIIType.EMAIL in result
        assert PIIType.PHONE in result

    def test_no_pii_detected(self):
        """Test clean text with no PII."""
        text = "This is a normal text about machine learning"
        result = PIIDetector.detect(text)

        assert len(result) == 0

    def test_redact_pii(self):
        """Test PII redaction."""
        text = "Email me at test@example.com"
        found_pii = PIIDetector.detect(text)
        redacted = PIIDetector.redact(text, found_pii)

        assert "test@example.com" not in redacted
        assert "[REDACTED_EMAIL]" in redacted

    def test_count_pii(self):
        """Test PII counting."""
        text = "Contact a@b.com and c@d.com, call 06.12.34.56.78"
        found_pii = PIIDetector.detect(text)
        count = PIIDetector.count_pii(found_pii)

        assert count >= 3

    def test_ssn_detection(self):
        """Test French social security number detection."""
        text = "Mon numéro de sécu est 1850175758035053"
        result = PIIDetector.detect(text)

        assert PIIType.SSN in result


class TestPIIEdgeCases:
    """Edge cases for PII detection."""

    def test_empty_string(self):
        """Test empty string handling."""
        result = PIIDetector.detect("")
        assert len(result) == 0

    def test_special_characters(self):
        """Test special characters handling."""
        text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = PIIDetector.detect(text)
        # Should not crash, may detect @ as part of email pattern
        assert isinstance(result, dict)

    def test_unicode_text(self):
        """Test unicode text handling."""
        text = "Bonjour, je suis là 日本語 中文"
        result = PIIDetector.detect(text)
        assert isinstance(result, dict)

    def test_case_insensitive_keywords(self):
        """Test case insensitivity for name keywords."""
        text = "MY NAME IS JOHN"
        result = PIIDetector.detect(text)
        assert PIIType.NAME in result
