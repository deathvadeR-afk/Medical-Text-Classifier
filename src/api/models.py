"""
Pydantic models for API request/response schemas with enhanced validation.
"""
import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    """Request model for medical text classification with security validation."""
    text: str = Field(
        ...,
        description="Medical text to classify",
        min_length=1,
        max_length=5000,
        json_schema_extra={"example": "What are the symptoms of diabetes?"}
    )

    @field_validator('text')
    @classmethod
    def validate_text_content(cls, v):
        """Validate text content for security."""
        # Allow whitespace-only text (will be handled by API logic)
        # Only check if text is completely empty (no characters at all)
        if v is None or (isinstance(v, str) and len(v) == 0):
            raise ValueError("Text cannot be empty")

        # Remove null bytes
        v = v.replace('\x00', '')

        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'data:.*base64',  # Data URLs with base64
            r'vbscript:',  # VBScript protocol
            r'on\w+\s*=',  # Event handlers (onclick, onload, etc.)
            r'expression\s*\(',  # CSS expressions
            r'eval\s*\(',  # JavaScript eval
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'insert\s+into',  # SQL injection
            r'delete\s+from',  # SQL injection
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Text contains potentially malicious content")

        # Check for excessive special characters (potential injection)
        special_char_ratio = sum(1 for c in v if not c.isalnum() and not c.isspace()) / len(v)
        if special_char_ratio > 0.3:  # More than 30% special characters
            raise ValueError("Text contains too many special characters")

        return v


class PredictionResponse(BaseModel):
    """Response model for medical text classification."""
    predicted_class: str = Field(
        ...,
        description="Predicted medical focus area"
    )
    confidence: float = Field(
        ...,
        description="Prediction confidence score",
        ge=0.0,
        le=1.0
    )
    probabilities: Dict[str, float] = Field(
        ...,
        description="Probability scores for all classes"
    )

    @field_validator('probabilities')
    @classmethod
    def validate_probabilities(cls, v):
        """Validate probability scores."""
        if not isinstance(v, dict):
            raise ValueError("Probabilities must be a dictionary")

        for class_name, prob in v.items():
            if not isinstance(prob, (int, float)):
                raise ValueError(f"Probability for {class_name} must be a number")
            if not 0.0 <= prob <= 1.0:
                raise ValueError(f"Probability for {class_name} must be between 0 and 1")

        return v


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="healthy")
    model_loaded: bool = Field(default=False)
    database_connected: bool = Field(default=False)
    security_enabled: bool = Field(default=True, description="Whether security features are enabled")
    rate_limiting_enabled: bool = Field(default=True, description="Whether rate limiting is enabled")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


class SecurityEventRequest(BaseModel):
    """Request model for security event reporting."""
    event_type: str = Field(..., description="Type of security event")
    severity: str = Field(..., description="Event severity level")
    details: Dict[str, Any] = Field(..., description="Event details")

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v):
        """Validate event type."""
        allowed_types = [
            'rate_limit_exceeded', 'invalid_input', 'authentication_failure',
            'suspicious_activity', 'access_denied', 'malicious_request'
        ]
        if v not in allowed_types:
            raise ValueError(f"Event type must be one of: {allowed_types}")
        return v

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level."""
        allowed_severities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_severities:
            raise ValueError(f"Severity must be one of: {allowed_severities}")
        return v


class APIKeyRequest(BaseModel):
    """Request model for API key validation."""
    api_key: str = Field(..., description="API key to validate", min_length=10)

    @field_validator('api_key')
    @classmethod
    def validate_api_key_format(cls, v):
        """Validate API key format."""
        # Remove whitespace
        v = v.strip()

        # Check for basic format (alphanumeric and some special chars)
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', v):
            raise ValueError("API key contains invalid characters")

        return v


class RateLimitInfo(BaseModel):
    """Response model for rate limit information."""
    requests_remaining: int = Field(..., description="Requests remaining in current window")
    reset_time: int = Field(..., description="Unix timestamp when rate limit resets")
    limit: int = Field(..., description="Maximum requests per window")
    window_seconds: int = Field(..., description="Rate limit window in seconds")
