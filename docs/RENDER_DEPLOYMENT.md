# 🚀 Render Deployment Guide
## Medical Text Classification App

Complete guide for deploying the Medical Text Classification application to Render.com.

## 📋 Prerequisites

1. **GitHub Repository**: Fork or clone this repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Model Files**: Ensure all model files are in the `models/` directory
4. **Environment Setup**: Review and configure environment variables

## 🎯 Quick Start (Recommended)

### Step 1: Prepare Your Repository

1. **Fork this repository** to your GitHub account
2. **Ensure model files are present**:
   ```
   models/
   ├── model.pt                 # PyTorch model weights
   ├── tokenizer.json           # Tokenizer configuration
   ├── tokenizer_config.json    # Tokenizer settings
   ├── vocab.txt               # Vocabulary file
   ├── special_tokens_map.json # Special tokens
   ├── label_mapping.json      # Label mappings
   └── reverse_label_mapping.json
   ```

3. **Commit and push** any changes to your repository

### Step 2: Deploy to Render

#### Option A: One-Click Deploy (Coming Soon)
Click the deploy button in the main README when available.

#### Option B: Manual Setup

1. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)
2. **Connect GitHub**: Link your GitHub account if not already connected

### Step 3: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `medtext-db`
   - **Database**: `medtext_prod`
   - **User**: `medtext_user`
   - **Region**: `Oregon` (or closest to your users)
   - **PostgreSQL Version**: `15`
   - **Plan**: `Starter` ($7/month)
3. Click **"Create Database"**
4. **Note the connection details** (you'll need the internal database URL)

### Step 4: Deploy API Backend

1. Click **"New +"** → **"Web Service"**
2. **Connect Repository**: Select your forked repository
3. **Configure Service**:
   - **Name**: `medtext-api`
   - **Environment**: `Docker`
   - **Region**: Same as database (`Oregon`)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Build Command**: Leave empty (Docker handles this)
   - **Start Command**: Leave empty (Docker handles this)

4. **Environment Variables** (click "Advanced" → "Environment Variables"):
   ```
   # Application
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   
   # Database (Render will provide this automatically)
   DATABASE_URL=[Auto-filled by Render when you connect the database]
   
   # Security - GENERATE STRONG VALUES
   SECRET_KEY=your-super-secret-jwt-key-64-chars-minimum-here
   REQUIRE_API_KEY=true
   API_KEYS=prod-api-key-1,prod-api-key-2,prod-api-key-3
   
   # CORS - UPDATE WITH YOUR ACTUAL DOMAINS
   ALLOWED_ORIGINS=https://medtext-frontend.onrender.com
   ALLOWED_HOSTS=medtext-api.onrender.com
   
   # Rate Limiting
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=3600
   
   # Security Features
   ENABLE_SECURITY_HEADERS=true
   MAX_TEXT_LENGTH=5000
   MIN_TEXT_LENGTH=1
   LOG_REQUESTS=true
   LOG_SENSITIVE_DATA=false
   ```

5. **Connect Database**:
   - In "Environment Variables" section
   - Click "Add from Database"
   - Select your `medtext-db` database
   - This automatically adds `DATABASE_URL`

6. **Advanced Settings**:
   - **Plan**: `Standard` ($25/month) - recommended for production
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes`

7. Click **"Create Web Service"**

### Step 5: Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. **Connect Repository**: Select the same repository
3. **Configure Site**:
   - **Name**: `medtext-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `build`

4. **Environment Variables**:
   ```
   NODE_ENV=production
   REACT_APP_API_URL=https://medtext-api.onrender.com
   REACT_APP_ENVIRONMENT=production
   ```

5. **Advanced Settings**:
   - **Auto-Deploy**: `Yes`
   - **Pull Request Previews**: `No` (optional)

6. Click **"Create Static Site"**

## 🔧 Configuration Details

### Environment Variables Reference

#### Required for API Service
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-provided by Render |
| `SECRET_KEY` | JWT secret key (64+ chars) | `your-super-secret-key...` |
| `ALLOWED_ORIGINS` | Frontend URLs for CORS | `https://yourdomain.com` |
| `ALLOWED_HOSTS` | API domain names | `api.yourdomain.com` |

#### Security Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `REQUIRE_API_KEY` | `true` | Enable API key authentication |
| `API_KEYS` | - | Comma-separated API keys |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per time window |
| `RATE_LIMIT_WINDOW` | `3600` | Time window in seconds |
| `ENABLE_SECURITY_HEADERS` | `true` | Enable security headers |

#### Optional Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_TEXT_LENGTH` | `5000` | Maximum input text length |
| `UVICORN_WORKERS` | `4` | Number of worker processes |

### Generating Secure Values

#### Secret Key (64+ characters)
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### API Keys
```bash
python -c "import secrets; print(','.join([secrets.token_urlsafe(32) for _ in range(3)]))"
```

## 🔍 Verification and Testing

### Step 1: Check Service Health

1. **API Health Check**:
   - Visit: `https://medtext-api.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

2. **Frontend Access**:
   - Visit: `https://medtext-frontend.onrender.com`
   - Should load the React application

3. **API Documentation**:
   - Visit: `https://medtext-api.onrender.com/docs`
   - Should show FastAPI Swagger UI

### Step 2: Test API Functionality

#### Test Prediction Endpoint
```bash
curl -X POST "https://medtext-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"text": "What are the symptoms of diabetes?"}'
```

Expected response:
```json
{
  "predicted_class": 3,
  "confidence": 0.95,
  "focus_group": "Metabolic & Endocrine Disorders",
  "probabilities": [0.01, 0.02, 0.01, 0.95, 0.01]
}
```

### Step 3: Monitor Deployment

1. **Check Logs**:
   - Go to Render Dashboard
   - Select your service
   - Click "Logs" tab
   - Look for any errors or warnings

2. **Monitor Metrics**:
   - Check "Metrics" tab for CPU/Memory usage
   - Verify response times are acceptable
   - Monitor error rates

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Build Failures

**Error**: `Failed to build Docker image`
```
Solution:
1. Check Dockerfile syntax
2. Verify all required files are in repository
3. Check build logs for specific errors
4. Ensure model files are present and accessible
```

#### 2. Database Connection Issues

**Error**: `Could not connect to database`
```
Solution:
1. Verify DATABASE_URL is set correctly
2. Check database service is running
3. Ensure database and API are in same region
4. Check database credentials
```

#### 3. Model Loading Errors

**Error**: `Model files not found`
```
Solution:
1. Verify all model files are in models/ directory
2. Check file permissions and sizes
3. Consider using Git LFS for large files
4. Verify model files are not in .gitignore
```

#### 4. CORS Errors

**Error**: `CORS policy blocked the request`
```
Solution:
1. Update ALLOWED_ORIGINS with correct frontend URL
2. Ensure protocol (https) matches
3. Check for trailing slashes in URLs
4. Verify CORS middleware is enabled
```

#### 5. Memory Issues

**Error**: `Container killed (OOMKilled)`
```
Solution:
1. Upgrade to higher plan (Standard → Pro)
2. Optimize model loading and memory usage
3. Reduce number of workers
4. Consider model quantization
```

### Getting Help

- **Render Support**: [help.render.com](https://help.render.com)
- **Community Forum**: [community.render.com](https://community.render.com)
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Status Page**: [status.render.com](https://status.render.com)

## 💰 Cost Breakdown

### Monthly Costs (USD)
- **PostgreSQL Starter**: $7/month
- **API Standard Plan**: $25/month
- **Frontend Static Site**: Free
- **Total**: ~$32/month

### Cost Optimization Tips
1. **Start small**: Begin with Starter plans and scale up
2. **Monitor usage**: Use Render's metrics to optimize resources
3. **Annual billing**: Consider annual plans for discounts
4. **Resource optimization**: Optimize code for better performance

## 🔄 Updates and Maintenance

### Automatic Deployments
- **Enabled by default** when you push to main branch
- **Build and deploy** process is automatic
- **Zero-downtime** deployments

### Manual Deployments
1. Go to Render Dashboard
2. Select your service
3. Click "Manual Deploy"
4. Choose "Deploy latest commit"

### Rollback Process
1. Go to service dashboard
2. Click "Deployments" tab
3. Find previous successful deployment
4. Click "Redeploy"

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Model files committed to repository
- [ ] Environment variables configured
- [ ] Security settings reviewed
- [ ] CORS origins updated
- [ ] API keys generated

### Post-Deployment
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Frontend loading correctly
- [ ] Database connected
- [ ] Logs reviewed for errors
- [ ] Performance metrics acceptable
- [ ] Security headers present
- [ ] SSL certificates active

### Ongoing Maintenance
- [ ] Monitor resource usage
- [ ] Review logs regularly
- [ ] Update dependencies
- [ ] Backup database
- [ ] Monitor costs
- [ ] Performance optimization

---

**🎉 Congratulations! Your Medical Text Classification app is now live on Render!**

**Access URLs:**
- **Frontend**: `https://medtext-frontend.onrender.com`
- **API**: `https://medtext-api.onrender.com`
- **API Docs**: `https://medtext-api.onrender.com/docs`
- **Health Check**: `https://medtext-api.onrender.com/health`
