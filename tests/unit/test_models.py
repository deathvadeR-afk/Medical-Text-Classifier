"""
Unit tests for Pydantic models.
"""
import pytest
from pydantic import ValidationError

from src.api.models import (
    PredictionRequest, 
    PredictionResponse, 
    HealthResponse, 
    ErrorResponse
)


class TestPredictionRequest:
    """Test cases for PredictionRequest model."""
    
    @pytest.mark.unit
    def test_valid_request(self):
        """Test valid prediction request."""
        request = PredictionRequest(text="What are the symptoms of diabetes?")
        assert request.text == "What are the symptoms of diabetes?"
    
    @pytest.mark.unit
    def test_empty_text_validation(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(text="")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
    
    @pytest.mark.unit
    def test_text_too_long_validation(self):
        """Test that text longer than max_length raises validation error."""
        long_text = "a" * 5001  # Exceeds max_length of 5000
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(text=long_text)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
    
    @pytest.mark.unit
    def test_missing_text_validation(self):
        """Test that missing text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
    
    @pytest.mark.unit
    def test_whitespace_only_text(self):
        """Test that whitespace-only text is valid (will be handled by API logic)."""
        request = PredictionRequest(text="   ")
        assert request.text == "   "
    
    @pytest.mark.unit
    def test_unicode_text(self):
        """Test that unicode text is handled correctly."""
        unicode_text = "¿Cuáles son los síntomas de la diabetes? 糖尿病の症状は何ですか？"
        request = PredictionRequest(text=unicode_text)
        assert request.text == unicode_text


class TestPredictionResponse:
    """Test cases for PredictionResponse model."""
    
    @pytest.mark.unit
    def test_valid_response(self):
        """Test valid prediction response."""
        response = PredictionResponse(
            predicted_class="Metabolic & Endocrine Disorders",
            confidence=0.85,
            probabilities={
                "Metabolic & Endocrine Disorders": 0.85,
                "Cardiovascular Diseases": 0.10,
                "Neurological & Cognitive Disorders": 0.03,
                "Cancers": 0.01,
                "Other Age-Related & Immune Disorders": 0.01
            }
        )
        assert response.predicted_class == "Metabolic & Endocrine Disorders"
        assert response.confidence == 0.85
        assert len(response.probabilities) == 5
    
    @pytest.mark.unit
    def test_confidence_bounds_validation(self):
        """Test that confidence must be between 0.0 and 1.0."""
        # Test confidence too low
        with pytest.raises(ValidationError) as exc_info:
            PredictionResponse(
                predicted_class="Test",
                confidence=-0.1,
                probabilities={}
            )
        assert "greater_than_equal" in str(exc_info.value)
        
        # Test confidence too high
        with pytest.raises(ValidationError) as exc_info:
            PredictionResponse(
                predicted_class="Test",
                confidence=1.1,
                probabilities={}
            )
        assert "less_than_equal" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_edge_confidence_values(self):
        """Test edge values for confidence (0.0 and 1.0)."""
        # Test minimum confidence
        response_min = PredictionResponse(
            predicted_class="Test",
            confidence=0.0,
            probabilities={}
        )
        assert response_min.confidence == 0.0
        
        # Test maximum confidence
        response_max = PredictionResponse(
            predicted_class="Test",
            confidence=1.0,
            probabilities={}
        )
        assert response_max.confidence == 1.0
    
    @pytest.mark.unit
    def test_missing_required_fields(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            PredictionResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # predicted_class, confidence, probabilities
        error_fields = [error["loc"][0] for error in errors]
        assert "predicted_class" in error_fields
        assert "confidence" in error_fields
        assert "probabilities" in error_fields


class TestHealthResponse:
    """Test cases for HealthResponse model."""
    
    @pytest.mark.unit
    def test_default_values(self):
        """Test default values for health response."""
        response = HealthResponse()
        assert response.status == "healthy"
        assert response.model_loaded is False
        assert response.database_connected is False
    
    @pytest.mark.unit
    def test_custom_values(self):
        """Test custom values for health response."""
        response = HealthResponse(
            status="unhealthy",
            model_loaded=True,
            database_connected=True
        )
        assert response.status == "unhealthy"
        assert response.model_loaded is True
        assert response.database_connected is True
    
    @pytest.mark.unit
    def test_partial_initialization(self):
        """Test partial initialization with some custom values."""
        response = HealthResponse(model_loaded=True)
        assert response.status == "healthy"  # default
        assert response.model_loaded is True  # custom
        assert response.database_connected is False  # default


class TestErrorResponse:
    """Test cases for ErrorResponse model."""
    
    @pytest.mark.unit
    def test_error_only(self):
        """Test error response with only error message."""
        response = ErrorResponse(error="Something went wrong")
        assert response.error == "Something went wrong"
        assert response.detail is None
    
    @pytest.mark.unit
    def test_error_with_detail(self):
        """Test error response with error and detail."""
        response = ErrorResponse(
            error="Validation failed",
            detail="Text field cannot be empty"
        )
        assert response.error == "Validation failed"
        assert response.detail == "Text field cannot be empty"
    
    @pytest.mark.unit
    def test_missing_error_validation(self):
        """Test that missing error field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"][0] == "error"
        assert errors[0]["type"] == "missing"
    
    @pytest.mark.unit
    def test_empty_error_validation(self):
        """Test that empty error string is still valid."""
        response = ErrorResponse(error="")
        assert response.error == ""


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    @pytest.mark.unit
    def test_prediction_request_json(self):
        """Test PredictionRequest JSON serialization."""
        request = PredictionRequest(text="Test medical text")
        json_data = request.model_dump()
        assert json_data == {"text": "Test medical text"}
        
        # Test deserialization
        new_request = PredictionRequest.model_validate(json_data)
        assert new_request.text == "Test medical text"
    
    @pytest.mark.unit
    def test_prediction_response_json(self):
        """Test PredictionResponse JSON serialization."""
        response = PredictionResponse(
            predicted_class="Test Category",
            confidence=0.75,
            probabilities={"Test Category": 0.75, "Other": 0.25}
        )
        json_data = response.model_dump()
        expected = {
            "predicted_class": "Test Category",
            "confidence": 0.75,
            "probabilities": {"Test Category": 0.75, "Other": 0.25}
        }
        assert json_data == expected
        
        # Test deserialization
        new_response = PredictionResponse.model_validate(json_data)
        assert new_response.predicted_class == "Test Category"
        assert new_response.confidence == 0.75
        assert new_response.probabilities == {"Test Category": 0.75, "Other": 0.25}
