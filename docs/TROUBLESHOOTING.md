# 🔧 Troubleshooting Guide
## Medical Text Classification App

Comprehensive troubleshooting guide for common issues, error resolution, and system maintenance.

## 🚨 Common Issues

### 1. Application Startup Issues

#### Problem: API Server Won't Start
**Symptoms:**
- `uvicorn` command fails
- Port already in use errors
- Module import errors

**Solutions:**
```bash
# Check if port is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process using port
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Check Python path and modules
python -c "import sys; print(sys.path)"
python -c "from src.api.main import app; print('Import successful')"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Problem: Frontend Won't Start
**Symptoms:**
- `npm start` fails
- Dependency resolution errors
- Port 3000 already in use

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Use different port
PORT=3001 npm start

# Check Node.js version
node --version  # Should be 18+
npm --version
```

### 2. Model Loading Issues

#### Problem: Model Files Not Found
**Symptoms:**
- `FileNotFoundError` for model files
- Model loading timeouts
- Prediction endpoint returns 500 errors

**Solutions:**
```bash
# Verify model files exist
ls -la models/
# Should contain: model.pt, tokenizer.json, label_mapping.json, etc.

# Check file permissions
chmod 644 models/*

# Verify model integrity
python -c "
import torch
model = torch.load('models/model.pt', map_location='cpu')
print('Model loaded successfully')
"

# Re-download models if corrupted
# (You may need to download from your training environment)
```

#### Problem: CUDA/GPU Issues
**Symptoms:**
- CUDA out of memory errors
- GPU not detected
- Slow inference times

**Solutions:**
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Install CPU-only PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Monitor GPU memory
nvidia-smi  # If NVIDIA GPU
```

### 3. Database Connection Issues

#### Problem: PostgreSQL Connection Failed
**Symptoms:**
- `psycopg2.OperationalError`
- Connection timeout errors
- Authentication failures

**Solutions:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Test connection manually
psql postgresql://meduser:medpass123@localhost:5432/medical_db

# Check environment variables
echo $DATABASE_URL

# Reset database connection
python -c "
from src.db import engine
try:
    with engine.connect() as conn:
        print('Database connection successful')
except Exception as e:
    print(f'Connection failed: {e}')
"

# Recreate database tables
python -c "
from src.db import init_db
init_db()
print('Database initialized')
"
```

#### Problem: SQLite Permission Issues
**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- Permission denied errors
- Database file corruption

**Solutions:**
```bash
# Check file permissions
ls -la *.db

# Fix permissions
chmod 664 medical.db

# Remove lock file
rm -f medical.db-wal medical.db-shm

# Recreate database
rm medical.db
python -c "from src.db import init_db; init_db()"
```

### 4. API Request Issues

#### Problem: CORS Errors
**Symptoms:**
- Browser console shows CORS errors
- Preflight request failures
- Cross-origin request blocked

**Solutions:**
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/predict

# Update ALLOWED_ORIGINS environment variable
export ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"

# Verify CORS middleware is enabled
python -c "
from src.api.main import app
print([middleware for middleware in app.user_middleware])
"
```

#### Problem: Rate Limiting Issues
**Symptoms:**
- 429 Too Many Requests errors
- Requests being blocked unexpectedly
- Rate limit headers missing

**Solutions:**
```bash
# Check rate limit configuration
curl -I http://localhost:8000/predict

# Reset rate limit (if using Redis)
redis-cli FLUSHALL

# Adjust rate limit settings
export RATE_LIMIT_REQUESTS=1000
export RATE_LIMIT_WINDOW=3600

# Disable rate limiting for testing
export RATE_LIMIT_REQUESTS=999999
```

#### Problem: Authentication Failures
**Symptoms:**
- 401 Unauthorized errors
- API key not recognized
- JWT token invalid

**Solutions:**
```bash
# Test without API key (development)
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"text": "test"}'

# Test with API key
curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{"text": "test"}'

# Check API key configuration
python -c "
import os
print(f'API Keys: {os.getenv(\"API_KEYS\")}')
print(f'Require API Key: {os.getenv(\"REQUIRE_API_KEY\")}')
"
```

### 5. Performance Issues

#### Problem: Slow Response Times
**Symptoms:**
- API responses taking >5 seconds
- Frontend loading slowly
- High CPU/memory usage

**Solutions:**
```bash
# Monitor system resources
top  # Linux/macOS
htop  # Enhanced version
Task Manager  # Windows

# Profile API performance
python -m cProfile -o profile.stats -c "
import requests
response = requests.post('http://localhost:8000/predict', 
                        json={'text': 'test text'})
"

# Check database query performance
python -c "
import time
from src.db import SessionLocal
start = time.time()
with SessionLocal() as db:
    # Your query here
    pass
print(f'Query time: {time.time() - start:.3f}s')
"

# Optimize model inference
# Consider model quantization or smaller batch sizes
```

#### Problem: Memory Leaks
**Symptoms:**
- Memory usage continuously increasing
- Out of memory errors
- System becomes unresponsive

**Solutions:**
```bash
# Monitor memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Use memory profiler
pip install memory-profiler
python -m memory_profiler your_script.py

# Check for circular references
import gc
gc.collect()
print(f'Garbage collected: {gc.collect()} objects')
```

## 🔍 Debugging Tools

### 1. Logging Configuration

#### Enable Debug Logging
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# For specific modules
logging.getLogger('src.ml.model').setLevel(logging.DEBUG)
logging.getLogger('src.api.main').setLevel(logging.DEBUG)
```

#### Log Analysis
```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep -i error logs/app.log

# Filter by timestamp
grep "2024-01-15" logs/app.log | grep ERROR
```

### 2. Health Check Diagnostics

#### Comprehensive Health Check
```bash
curl -s http://localhost:8000/health | jq '.'
```

#### Component-Specific Checks
```python
# Database health
python -c "
from src.db import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database: OK')
except Exception as e:
    print(f'Database: ERROR - {e}')
"

# Model health
python -c "
from src.ml.model import MedicalTextClassifier
try:
    classifier = MedicalTextClassifier()
    result = classifier.predict('test')
    print('Model: OK')
except Exception as e:
    print(f'Model: ERROR - {e}')
"
```

### 3. API Testing Tools

#### cURL Examples
```bash
# Health check
curl -v http://localhost:8000/health

# Prediction with verbose output
curl -v -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -H "X-API-Key: test-key" \
     -d '{"text": "What are the symptoms of diabetes?"}'

# Check metrics
curl http://localhost:8000/metrics
```

#### Python Testing Script
```python
import requests
import time

def test_api_endpoint():
    url = "http://localhost:8000/predict"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
    }
    data = {"text": "Test medical text"}
    
    start_time = time.time()
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoint()
    print(f"Test {'PASSED' if success else 'FAILED'}")
```

## 🐳 Docker Troubleshooting

### Container Issues

#### Problem: Container Won't Start
```bash
# Check container logs
docker logs medtext-api

# Check container status
docker ps -a

# Inspect container configuration
docker inspect medtext-api

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Problem: Container Resource Issues
```bash
# Check resource usage
docker stats

# Increase memory limits
# In docker-compose.yml:
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### Network Issues

#### Problem: Service Communication
```bash
# Check network connectivity
docker network ls
docker network inspect medtext_default

# Test inter-service communication
docker exec medtext-api ping medtext-postgres

# Check port mappings
docker port medtext-api
```

## 📊 Monitoring and Alerting

### Prometheus Metrics

#### Check Metrics Collection
```bash
# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query specific metrics
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'
```

### Grafana Dashboards

#### Dashboard Issues
```bash
# Check Grafana logs
docker logs medtext-grafana

# Reset admin password
docker exec -it medtext-grafana grafana-cli admin reset-admin-password admin

# Import dashboard manually
# Go to http://localhost:3001 → Import → Upload JSON
```

## 🔒 Security Troubleshooting

### SSL/TLS Issues

#### Certificate Problems
```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443

# Verify certificate chain
curl -vI https://yourdomain.com

# Test with insecure connection (debugging only)
curl -k https://yourdomain.com/health
```

### Authentication Issues

#### API Key Problems
```bash
# Test API key validation
python -c "
from src.api.security import verify_api_key
result = verify_api_key('your-api-key')
print(f'API Key Valid: {result}')
"

# Check environment variables
env | grep API_KEY
```

## 📱 Frontend Troubleshooting

### React Development Issues

#### Build Failures
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Check for conflicting dependencies
npm ls

# Update dependencies
npm update
```

#### Runtime Errors
```bash
# Check browser console for errors
# Open Developer Tools → Console

# Enable React DevTools
# Install React Developer Tools browser extension

# Check network requests
# Developer Tools → Network tab
```

## 🆘 Getting Help

### 1. Check Documentation
- [Installation Guide](INSTALLATION.md)
- [API Documentation](API.md)
- [Security Guide](SECURITY.md)
- [Monitoring Guide](MONITORING.md)

### 2. Search Issues
- Check [GitHub Issues](https://github.com/YOUR_USERNAME/Medical-Text-Classification/issues)
- Search for similar problems
- Check closed issues for solutions

### 3. Create Support Request

When creating an issue, include:

#### System Information
```bash
# Operating system
uname -a  # Linux/macOS
systeminfo  # Windows

# Python version
python --version

# Node.js version
node --version

# Docker version
docker --version
```

#### Error Information
- Complete error messages
- Stack traces
- Log files
- Steps to reproduce
- Expected vs actual behavior

#### Environment Details
- Environment variables (sanitized)
- Configuration files
- Recent changes
- Network setup

### 4. Emergency Contacts

For critical production issues:
- **Slack**: #medical-text-classification
- **Email**: support@yourcompany.com
- **On-call**: +1-XXX-XXX-XXXX

---

## 🎯 Prevention Tips

### 1. **Regular Maintenance**
- Update dependencies monthly
- Monitor system resources
- Review logs weekly
- Test backups regularly

### 2. **Monitoring Setup**
- Set up alerts for critical metrics
- Monitor error rates and response times
- Track resource usage trends
- Implement health checks

### 3. **Documentation**
- Keep troubleshooting logs
- Document custom configurations
- Update runbooks regularly
- Share knowledge with team

### 4. **Testing**
- Run tests before deployments
- Test in staging environment
- Validate configuration changes
- Monitor after deployments

This troubleshooting guide should help you quickly identify and resolve common issues with the Medical Text Classification application.
