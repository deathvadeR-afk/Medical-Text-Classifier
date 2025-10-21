# Medical Text Classification API - Monitoring & Observability

This document describes the comprehensive monitoring and observability setup for the Medical Text Classification API.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **FastAPI Metrics**: Application-level metrics
- **Health Checks**: Service availability monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───►│   Prometheus    │───►│    Grafana      │
│   (Port 8000)   │    │   (Port 9090)   │    │   (Port 3001)   │
│                 │    │                 │    │                 │
│ Metrics Server  │    │ Scrapes metrics │    │ Visualizes data │
│   (Port 8001)   │    │ Stores data     │    │ Dashboards      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start all services including monitoring
docker-compose up -d

# Check services are running
docker-compose ps
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123`
- **Prometheus**: http://localhost:9090
- **API Metrics**: http://localhost:8001/metrics

## Metrics Collected

### Application Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|---------|
| `http_requests_total` | Counter | Total HTTP requests | `method`, `endpoint`, `status` |
| `http_request_duration_seconds` | Histogram | HTTP request duration | - |
| `predictions_total` | Counter | Total ML predictions | `predicted_class` |
| `prediction_duration_seconds` | Histogram | ML prediction duration | - |
| `prediction_confidence` | Histogram | Prediction confidence scores | - |
| `model_loaded` | Gauge | Model loading status (1=loaded, 0=not loaded) | - |
| `database_connected` | Gauge | Database connection status (1=connected, 0=not connected) | - |
| `health_checks_total` | Counter | Total health check requests | `status` |

### System Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `up` | Gauge | Service availability (1=up, 0=down) |
| `prometheus_config_last_reload_successful` | Gauge | Prometheus config reload status |

## Dashboards

### 1. API Overview Dashboard
- **URL**: http://localhost:3001/d/medical-text-api-overview
- **Purpose**: High-level API performance monitoring
- **Panels**:
  - Request rate by endpoint
  - Response time percentiles
  - HTTP status code distribution
  - Error rates

### 2. ML Model Performance Dashboard
- **URL**: http://localhost:3001/d/medical-text-ml-performance
- **Purpose**: Machine learning model monitoring
- **Panels**:
  - Model loading status
  - Predictions by class distribution
  - Prediction latency metrics
  - Prediction confidence distribution

### 3. System Health Dashboard
- **URL**: http://localhost:3001/d/medical-text-system-health
- **Purpose**: Infrastructure and service health
- **Panels**:
  - Service availability status
  - Database connection status
  - Health check frequency
  - System uptime

## Alerting Rules

### Critical Alerts

| Alert Name | Condition | Duration | Description |
|------------|-----------|----------|-------------|
| `APIDown` | `up{job="medical-text-api"} == 0` | 1m | API service is down |
| `ModelNotLoaded` | `model_loaded == 0` | 1m | ML model failed to load |

### Warning Alerts

| Alert Name | Condition | Duration | Description |
|------------|-----------|----------|-------------|
| `HighErrorRate` | `rate(http_requests_total{status=~"5.."}[5m]) > 0.1` | 2m | High 5xx error rate |
| `HighResponseTime` | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5` | 3m | High API response time |
| `HighPredictionLatency` | `histogram_quantile(0.95, rate(prediction_duration_seconds_bucket[5m])) > 3` | 2m | High ML prediction latency |
| `DatabaseDown` | `up{job="postgres"} == 0` | 2m | Database is down |

## Configuration Files

### Prometheus Configuration
- **File**: `monitoring/prometheus.yml`
- **Purpose**: Defines scrape targets and alerting rules
- **Key Settings**:
  - Scrape interval: 15s
  - API metrics endpoint: `host.docker.internal:8001`
  - Alert rules: `monitoring/alert_rules.yml`

### Grafana Configuration
- **Provisioning**: `monitoring/grafana/provisioning/`
- **Dashboards**: `monitoring/grafana/dashboards/`
- **Data Sources**: Automatically configured Prometheus connection

## Troubleshooting

### Common Issues

1. **Metrics not appearing in Grafana**
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify FastAPI metrics server is running on port 8001
   - Check docker network connectivity

2. **Dashboards not loading**
   - Verify Grafana provisioning configuration
   - Check dashboard JSON files are valid
   - Restart Grafana container: `docker-compose restart grafana`

3. **Alerts not firing**
   - Check Prometheus rules: http://localhost:9090/rules
   - Verify alert rule syntax in `monitoring/alert_rules.yml`
   - Check Prometheus logs: `docker-compose logs prometheus`

### Useful Commands

```bash
# Check metrics endpoint
curl http://localhost:8001/metrics

# Check health endpoint
curl http://localhost:8000/health

# View Prometheus targets
curl http://localhost:9090/api/v1/targets

# Restart monitoring stack
docker-compose restart prometheus grafana

# View logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

## Customization

### Adding New Metrics

1. Add metric definition in `src/api/main.py`:
```python
NEW_METRIC = Counter('new_metric_total', 'Description', ['label1', 'label2'])
```

2. Instrument your code:
```python
NEW_METRIC.labels(label1='value1', label2='value2').inc()
```

3. Update Grafana dashboards to visualize the new metric

### Adding New Alerts

1. Edit `monitoring/alert_rules.yml`
2. Add new alert rule following existing patterns
3. Restart Prometheus: `docker-compose restart prometheus`

### Creating Custom Dashboards

1. Create dashboard in Grafana UI
2. Export dashboard JSON
3. Save to `monitoring/grafana/dashboards/`
4. Restart Grafana to load automatically

## Best Practices

1. **Monitor Key Metrics**: Focus on request rate, error rate, and response time
2. **Set Appropriate Thresholds**: Base alerts on historical data and SLA requirements
3. **Use Labels Wisely**: Add meaningful labels but avoid high cardinality
4. **Regular Review**: Periodically review and update dashboards and alerts
5. **Documentation**: Keep monitoring documentation up to date

## Security Considerations

- Grafana admin credentials should be changed in production
- Prometheus metrics may contain sensitive information
- Consider authentication for monitoring endpoints in production
- Use HTTPS for external access to monitoring tools
