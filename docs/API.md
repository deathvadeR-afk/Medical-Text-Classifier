# 🔌 API Documentation
## Medical Text Classification API

Complete reference for the FastAPI-based medical text classification API with examples, authentication, and best practices.

## 🎯 Base Information

- **Base URL**: `http://localhost:8000` (development) / `https://medtext-api.onrender.com` (production)
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: API Key (optional in development, required in production)

## 🔐 Authentication

### API Key Authentication

For production environments, include the API key in the request header:

```bash
curl -H "X-API-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     https://medtext-api.onrender.com/predict
```

### Getting API Keys

API keys are configured via environment variables. Contact your system administrator for production keys.

## 📋 Endpoints Overview

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | System health check | No |
| `/predict` | POST | Classify medical text | Yes (prod) |
| `/metrics` | GET | Prometheus metrics | No |
| `/docs` | GET | Interactive API documentation | No |
| `/security/info` | GET | Security configuration info | No |

## 🔍 Detailed Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Returns the current health status of the API and its dependencies.

**Request**:
```bash
curl -X GET "http://localhost:8000/health"
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12.5
    },
    "model": {
      "status": "healthy",
      "model_loaded": true,
      "model_size_mb": 438.2
    },
    "security": {
      "rate_limiting": "enabled",
      "api_key_auth": "enabled",
      "security_headers": "enabled"
    }
  },
  "uptime_seconds": 86400,
  "request_count": 15420,
  "error_rate": 0.02
}
```

**Response Codes**:
- `200`: System is healthy
- `503`: System is unhealthy (check components for details)

### 2. Text Classification

**Endpoint**: `POST /predict`

**Description**: Classifies medical text into one of 5 focus groups with confidence scores.

**Request Headers**:
```
Content-Type: application/json
X-API-Key: your-api-key-here  # Required in production
```

**Request Body**:
```json
{
  "text": "What are the symptoms of diabetes and how is it diagnosed?"
}
```

**Request Example**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "text": "What are the symptoms of diabetes and how is it diagnosed?"
  }'
```

**Response**:
```json
{
  "predicted_class": 3,
  "confidence": 0.9847,
  "focus_group": "Metabolic & Endocrine Disorders",
  "probabilities": [
    0.0023,  // Neurological & Cognitive Disorders
    0.0045,  // Cancers
    0.0031,  // Cardiovascular Diseases
    0.9847,  // Metabolic & Endocrine Disorders
    0.0054   // Other Age-Related & Immune Disorders
  ],
  "processing_time_ms": 87.3,
  "model_version": "biomedbert-v1.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Focus Groups**:
| Class | Focus Group | Description |
|-------|-------------|-------------|
| 0 | Neurological & Cognitive Disorders | Alzheimer's, Parkinson's, dementia, brain disorders |
| 1 | Cancers | All types of cancer, oncology, tumors |
| 2 | Cardiovascular Diseases | Heart disease, hypertension, stroke, circulation |
| 3 | Metabolic & Endocrine Disorders | Diabetes, thyroid, hormones, metabolism |
| 4 | Other Age-Related & Immune Disorders | Arthritis, autoimmune, aging-related conditions |

**Response Codes**:
- `200`: Successful prediction
- `400`: Invalid input (text too long/short, malformed JSON)
- `401`: Unauthorized (missing or invalid API key)
- `422`: Validation error (invalid text content)
- `429`: Rate limit exceeded
- `500`: Internal server error

**Input Validation**:
- **Text length**: 1-5000 characters
- **Content**: Must not contain malicious patterns (XSS, SQL injection)
- **Format**: Valid UTF-8 text

### 3. Prometheus Metrics

**Endpoint**: `GET /metrics`

**Description**: Returns Prometheus-formatted metrics for monitoring.

**Request**:
```bash
curl -X GET "http://localhost:8000/metrics"
```

**Response** (excerpt):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/predict",status="200"} 1542.0

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1234.0
http_request_duration_seconds_bucket{le="0.5"} 1540.0

# HELP model_inference_duration_seconds Model inference time
# TYPE model_inference_duration_seconds histogram
model_inference_duration_seconds_bucket{le="0.05"} 890.0
model_inference_duration_seconds_bucket{le="0.1"} 1520.0

# HELP predictions_total Total predictions made
# TYPE predictions_total counter
predictions_total{focus_group="Metabolic & Endocrine Disorders"} 456.0
predictions_total{focus_group="Cardiovascular Diseases"} 234.0

# HELP rate_limit_violations_total Rate limit violations
# TYPE rate_limit_violations_total counter
rate_limit_violations_total 12.0
```

### 4. Security Information

**Endpoint**: `GET /security/info`

**Description**: Returns information about security configuration (non-sensitive).

**Request**:
```bash
curl -X GET "http://localhost:8000/security/info"
```

**Response**:
```json
{
  "rate_limiting": {
    "enabled": true,
    "requests_per_window": 100,
    "window_seconds": 3600
  },
  "authentication": {
    "api_key_required": true,
    "jwt_enabled": false
  },
  "security_headers": {
    "enabled": true,
    "headers": [
      "X-Frame-Options",
      "X-Content-Type-Options",
      "X-XSS-Protection",
      "Strict-Transport-Security",
      "Content-Security-Policy"
    ]
  },
  "input_validation": {
    "max_text_length": 5000,
    "min_text_length": 1,
    "xss_protection": true,
    "sql_injection_protection": true
  }
}
```

## 📊 Rate Limiting

### Default Limits
- **Development**: 1000 requests per hour per IP
- **Production**: 100 requests per hour per API key

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

### Rate Limit Exceeded Response
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600
}
```

## ❌ Error Handling

### Error Response Format
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid request format or parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Endpoint not found |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Input Validation Errors
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "Text must be between 1 and 5000 characters",
      "type": "value_error"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

## 🔧 SDK Examples

### Python SDK
```python
import requests
import json

class MedicalTextAPI:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def predict(self, text):
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    def health(self):
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage
api = MedicalTextAPI("https://medtext-api.onrender.com", "your-api-key")
result = api.predict("What are the symptoms of diabetes?")
print(f"Focus Group: {result['focus_group']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### JavaScript SDK
```javascript
class MedicalTextAPI {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async predict(text) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }
        
        const response = await fetch(`${this.baseUrl}/predict`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return response.json();
    }
    
    async health() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }
        return response.json();
    }
}

// Usage
const api = new MedicalTextAPI('https://medtext-api.onrender.com', 'your-api-key');
const result = await api.predict('What are the symptoms of diabetes?');
console.log(`Focus Group: ${result.focus_group}`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
```

### cURL Examples
```bash
# Health check
curl -X GET "https://medtext-api.onrender.com/health"

# Prediction with API key
curl -X POST "https://medtext-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"text": "What are the symptoms of diabetes?"}'

# Get metrics
curl -X GET "https://medtext-api.onrender.com/metrics"
```

## 🚀 Best Practices

### 1. Error Handling
- Always check HTTP status codes
- Implement retry logic with exponential backoff
- Handle rate limiting gracefully
- Log errors for debugging

### 2. Performance
- Reuse HTTP connections
- Implement client-side caching for repeated requests
- Use appropriate timeouts
- Monitor response times

### 3. Security
- Store API keys securely (environment variables)
- Use HTTPS in production
- Validate responses on client side
- Implement request signing for sensitive applications

### 4. Monitoring
- Track API usage and performance
- Monitor error rates and response times
- Set up alerts for API failures
- Use correlation IDs for request tracing

---

## 🎯 Interactive Documentation

For interactive API exploration, visit:
- **Development**: http://localhost:8000/docs
- **Production**: https://medtext-api.onrender.com/docs

The interactive documentation provides:
- Live API testing
- Request/response examples
- Schema validation
- Authentication testing
