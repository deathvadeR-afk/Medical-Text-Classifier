# Render Deployment Guide
## Medical Text Classification App

This guide will help you deploy the Medical Text Classification application to Render.com.

## 🚀 Quick Deployment

### Option 1: One-Click Deploy (Recommended)

1. **Fork this repository** to your GitHub account
2. **Click the Deploy to Render button** (add this to your main README):
   ```
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/Medical-Text-Classification)
   ```
3. **Configure environment variables** in the Render dashboard
4. **Deploy!** 🎉

### Option 2: Manual Setup

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account

#### Step 2: Create PostgreSQL Database
1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `medtext-postgres`
   - **Database**: `medtext_prod`
   - **User**: `medtext_user`
   - **Region**: Choose closest to your users
   - **Plan**: Start with **Starter** ($7/month)
3. Click **"Create Database"**
4. **Save the connection details** (you'll need them for the API service)

#### Step 3: Deploy API Backend
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `medtext-api`
   - **Environment**: `Docker`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: **Standard** ($25/month) or higher for production

4. **Environment Variables**:
   ```
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   
   # Database (get from your PostgreSQL service)
   POSTGRES_HOST=<your-postgres-host>
   POSTGRES_PORT=5432
   POSTGRES_DB=medtext_prod
   POSTGRES_USER=medtext_user
   POSTGRES_PASSWORD=<your-postgres-password>
   
   # Security (generate strong values)
   SECRET_KEY=<generate-64-char-secret>
   REQUIRE_API_KEY=true
   API_KEYS=<generate-api-keys>
   
   # CORS (update with your frontend URL)
   ALLOWED_ORIGINS=https://medtext-frontend.onrender.com
   ALLOWED_HOSTS=medtext-api.onrender.com
   
   # Rate Limiting
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=3600
   
   # Security Headers
   ENABLE_SECURITY_HEADERS=true
   MAX_TEXT_LENGTH=5000
   MIN_TEXT_LENGTH=1
   LOG_REQUESTS=true
   LOG_SENSITIVE_DATA=false
   ```

5. **Advanced Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 4`
   - **Health Check Path**: `/health`

6. Click **"Create Web Service"**

#### Step 4: Deploy Frontend
1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
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

5. Click **"Create Static Site"**

## 🔧 Configuration Details

### Required Files in Repository

Ensure these files are in your repository:

```
├── Dockerfile                 # API container
├── requirements.txt          # Python dependencies
├── src/                     # API source code
├── models/                  # ML model files
├── frontend/
│   ├── package.json         # Frontend dependencies
│   ├── src/                 # React source code
│   └── public/              # Static assets
└── deploy/render/
    ├── build.sh             # Build script
    ├── start.sh             # Start script
    └── README.md            # This file
```

### Model Files Setup

**Important**: Ensure your model files are included in the repository:

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

If model files are large (>100MB), consider using:
- **Git LFS** (Large File Storage)
- **External storage** (S3, Google Cloud Storage) with download script
- **Model registry** (Hugging Face Hub, MLflow)

### Environment Variables Reference

#### Required Variables
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `SECRET_KEY` (64+ characters)
- `ALLOWED_ORIGINS` (your frontend URL)
- `ALLOWED_HOSTS` (your API domain)

#### Security Variables
- `REQUIRE_API_KEY=true` (recommended for production)
- `API_KEYS` (comma-separated list)
- `RATE_LIMIT_REQUESTS=100`
- `RATE_LIMIT_WINDOW=3600`

#### Optional Variables
- `UVICORN_WORKERS=4` (adjust based on plan)
- `LOG_LEVEL=INFO`
- `MAX_TEXT_LENGTH=5000`

## 🔒 Security Considerations

### 1. Environment Variables
- **Never commit secrets** to your repository
- Use Render's environment variable management
- Generate strong, unique values for production

### 2. API Keys
```bash
# Generate secure API keys
openssl rand -hex 32
```

### 3. Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups (Render handles this)

### 4. CORS Configuration
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📊 Monitoring and Logging

### Built-in Monitoring
- Render provides built-in metrics and logs
- Access via Render dashboard → Service → Metrics/Logs

### Custom Monitoring
- API includes `/health` endpoint
- Prometheus metrics at `/metrics`
- Request logging enabled by default

### Log Access
```bash
# View logs via Render CLI
render logs -s medtext-api
render logs -s medtext-frontend
```

## 🚀 Scaling and Performance

### Vertical Scaling
- **Starter**: 0.5 CPU, 512MB RAM
- **Standard**: 1 CPU, 2GB RAM  
- **Pro**: 2 CPU, 4GB RAM
- **Pro Plus**: 4 CPU, 8GB RAM

### Horizontal Scaling
- Render automatically handles load balancing
- Consider upgrading plan for high traffic
- Database connection pooling included

### Performance Tips
1. **Use appropriate plan** for your traffic
2. **Enable caching** (Redis add-on available)
3. **Optimize model loading** (consider model quantization)
4. **Monitor response times** via Render dashboard

## 🔄 CI/CD and Updates

### Automatic Deployments
- **Auto-deploy** enabled by default
- Deploys on every push to main branch
- **Manual deploy** option available

### Deployment Process
1. Code push triggers build
2. Render builds Docker container
3. Health check validates deployment
4. Traffic switches to new version
5. Old version terminated

### Rollback
- **Instant rollback** via Render dashboard
- Previous deployments preserved
- Zero-downtime deployments

## 💰 Cost Estimation

### Monthly Costs (USD)
- **PostgreSQL Starter**: $7/month
- **API Standard**: $25/month  
- **Frontend Static**: $0 (free tier)
- **Total**: ~$32/month

### Cost Optimization
- Start with smaller plans
- Scale up based on usage
- Monitor resource utilization
- Consider annual billing for discounts

## 🆘 Troubleshooting

### Common Issues

#### 1. Model Loading Errors
```
Error: Model files not found
```
**Solution**: Ensure model files are in repository or accessible storage

#### 2. Database Connection Issues
```
Error: Could not connect to database
```
**Solution**: Check environment variables and database status

#### 3. Build Failures
```
Error: Requirements installation failed
```
**Solution**: Check requirements.txt and Python version compatibility

#### 4. Memory Issues
```
Error: Container killed (OOMKilled)
```
**Solution**: Upgrade to higher plan or optimize memory usage

### Getting Help
- **Render Support**: [help.render.com](https://help.render.com)
- **Community**: [community.render.com](https://community.render.com)
- **Documentation**: [render.com/docs](https://render.com/docs)

## 🎯 Production Checklist

- [ ] Model files included in repository
- [ ] Environment variables configured
- [ ] Database created and connected
- [ ] API service deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Monitoring and alerts set up
- [ ] Backup strategy confirmed
- [ ] Performance testing completed

---

**🎉 Your Medical Text Classification app is now live on Render!**

Access your application:
- **Frontend**: `https://medtext-frontend.onrender.com`
- **API**: `https://medtext-api.onrender.com`
- **API Docs**: `https://medtext-api.onrender.com/docs`
