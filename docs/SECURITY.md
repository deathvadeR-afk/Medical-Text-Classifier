# Security Implementation Guide

## Overview

The Medical Text Classification API implements comprehensive security measures to protect against common web application vulnerabilities and ensure safe operation in production environments.

## Security Features

### 🔐 Authentication & Authorization

#### API Key Authentication
- **Optional API key authentication** for production environments
- **Environment-based configuration** via `REQUIRE_API_KEY` and `API_KEYS`
- **Header-based authentication** using `X-API-Key` header
- **Multiple API keys support** for different clients/services

#### JWT Token Support
- **JWT token authentication** for user sessions
- **Configurable token expiration** (default: 30 minutes)
- **Secure token generation** using cryptographically secure random keys
- **Bearer token authentication** via Authorization header

### 🛡️ Input Validation & Sanitization

#### Text Input Validation
- **Length limits**: 1-5000 characters (configurable)
- **Content sanitization**: Removes null bytes and dangerous characters
- **Pattern detection**: Blocks script injection, SQL injection attempts
- **Special character limits**: Prevents excessive special character usage

#### Request Validation
- **Pydantic models** with strict validation rules
- **Type checking** for all input parameters
- **Format validation** for API keys and tokens
- **Automatic data sanitization** before processing

### 🚦 Rate Limiting

#### Request Rate Limiting
- **Configurable limits**: Default 100 requests per hour
- **Client-based tracking**: Uses IP address or X-Forwarded-For header
- **Sliding window**: Time-based request counting
- **Graceful responses**: Returns 429 status with retry information

#### Protection Scope
- **All endpoints protected** except health checks and metrics
- **Per-client tracking** to prevent abuse
- **Automatic cleanup** of old request records

### 🔒 Security Headers

#### HTTP Security Headers
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-XSS-Protection**: Enables browser XSS protection
- **Strict-Transport-Security**: Enforces HTTPS connections
- **Content-Security-Policy**: Restricts resource loading
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features

### 🌐 CORS Configuration

#### Cross-Origin Resource Sharing
- **Environment-based origins**: Configurable allowed origins
- **Restricted methods**: Only necessary HTTP methods allowed
- **Credential support**: Configurable credential handling
- **Header restrictions**: Limited allowed headers

### 🏠 Host Validation

#### Host Header Protection
- **DNS rebinding protection**: Validates Host header
- **Allowed hosts list**: Configurable trusted hosts
- **Automatic rejection**: Blocks requests with invalid hosts

### 📝 Security Logging

#### Comprehensive Logging
- **Request logging**: All requests logged with metadata
- **Security events**: Special logging for security violations
- **Client tracking**: IP address and user agent logging
- **Sensitive data protection**: Configurable sensitive data masking

## Configuration

### Environment Variables

```bash
# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here
REQUIRE_API_KEY=false
API_KEYS=api-key-1,api-key-2,api-key-3
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
ENABLE_SECURITY_HEADERS=true
MAX_TEXT_LENGTH=5000
MIN_TEXT_LENGTH=1
LOG_REQUESTS=true
LOG_SENSITIVE_DATA=false
```

### Production Configuration

```bash
# Production Security Settings
REQUIRE_API_KEY=true
API_KEYS=prod-key-1,prod-key-2
RATE_LIMIT_REQUESTS=50
ALLOWED_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production
```

## Security Best Practices

### 🔑 API Key Management

1. **Generate strong API keys**: Use cryptographically secure random generators
2. **Rotate keys regularly**: Implement key rotation schedule
3. **Limit key scope**: Use different keys for different services
4. **Monitor key usage**: Track API key usage patterns
5. **Revoke compromised keys**: Have a key revocation process

### 🛠️ Deployment Security

1. **Use HTTPS**: Always deploy with SSL/TLS encryption
2. **Secure headers**: Enable all security headers in production
3. **Rate limiting**: Set appropriate rate limits for your use case
4. **Input validation**: Never trust client input
5. **Error handling**: Don't expose sensitive information in errors

### 📊 Monitoring & Alerting

1. **Security metrics**: Monitor rate limit violations and security events
2. **Log analysis**: Regularly review security logs
3. **Anomaly detection**: Set up alerts for unusual patterns
4. **Incident response**: Have a security incident response plan

## Security Testing

### Running Security Tests

```bash
# Run all security tests
pytest tests/security/ -v

# Run specific security test categories
pytest tests/security/test_security.py::TestInputValidation -v
pytest tests/security/test_security.py::TestRateLimiting -v
pytest tests/security/test_security.py::TestAPIKeyAuthentication -v
```

### Test Coverage

- ✅ Input validation and sanitization
- ✅ Rate limiting enforcement
- ✅ API key authentication
- ✅ Security headers presence
- ✅ Host validation
- ✅ Error handling security
- ✅ CORS configuration

## Security Endpoints

### Security Information
```
GET /security/info
```
Returns current security configuration and status.

### Health Check with Security
```
GET /health
```
Includes security status in health check response.

## Vulnerability Prevention

### Prevented Attack Types

- **Cross-Site Scripting (XSS)**: Input sanitization and CSP headers
- **SQL Injection**: Input validation and parameterized queries
- **Cross-Site Request Forgery (CSRF)**: Security headers and origin validation
- **Clickjacking**: X-Frame-Options header
- **MIME Type Confusion**: X-Content-Type-Options header
- **DNS Rebinding**: Host header validation
- **Rate Limiting Bypass**: Client-based tracking
- **Information Disclosure**: Secure error handling

### Security Metrics

The API exposes security-related Prometheus metrics:

- `rate_limit_violations_total`: Rate limit violation attempts
- `security_events_total`: Security events by type
- `api_key_failures_total`: Failed API key authentications
- `invalid_inputs_total`: Invalid input attempts by type

## Incident Response

### Security Event Types

1. **Rate Limit Exceeded**: Client exceeded request limits
2. **Invalid Input**: Malicious input detected
3. **Authentication Failure**: Invalid API key or token
4. **Suspicious Activity**: Unusual request patterns
5. **Access Denied**: Unauthorized access attempts
6. **Malicious Request**: Detected attack patterns

### Response Actions

1. **Log the event**: All security events are automatically logged
2. **Block the client**: Rate limiting automatically blocks abusive clients
3. **Alert administrators**: Set up monitoring alerts for critical events
4. **Investigate patterns**: Analyze logs for attack patterns
5. **Update defenses**: Adjust security rules based on threats

## Compliance

### Security Standards

- **OWASP Top 10**: Protection against common web vulnerabilities
- **Input Validation**: Comprehensive input sanitization
- **Authentication**: Secure API key and JWT token handling
- **Authorization**: Proper access control implementation
- **Logging**: Comprehensive security event logging
- **Error Handling**: Secure error responses

### Data Protection

- **No sensitive data storage**: API doesn't store personal information
- **Request logging**: Configurable sensitive data masking
- **Secure transmission**: HTTPS enforcement in production
- **Input sanitization**: All inputs cleaned before processing
