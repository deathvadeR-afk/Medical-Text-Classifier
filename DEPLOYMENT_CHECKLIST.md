# ✅ Render Deployment Checklist
## Medical Text Classification App

**Everything you need to deploy successfully to Render.com**

---

## 🎯 **Pre-Deployment Checklist**

### **✅ Repository Ready**
- [x] Code is on GitHub
- [x] Model files are present in `models/` directory
- [x] `render.yaml` blueprint file exists
- [x] Dockerfile is configured
- [x] Frontend build configuration ready

### **✅ Secrets Generated**
Your secure secrets (from `generate_render_secrets.py`):

```bash
SECRET_KEY=-RCnLrYqo1C6PhsILArnLsWYFpm76CurtittFFV2tP0r1JComao7PYli-w73iFphhzmzCRQTk8zQh0nWZZICbA

API_KEYS=T3z3cJCQ78KeX_IGqit64tbrJxZzF5TKGSsIdn1me3Y,w1MWe-NgaXB5hx7_URAiqfX7aH0moXL0YMiPMcdkGOQ,trOjQH4sPwUAsJVOpZjY5r8G037nzxXIjo2EAX3i0Ss
```

**⚠️ IMPORTANT: Keep these secrets secure! Don't share them publicly.**

---

## 🚀 **Deployment Steps**

### **Step 1: Create Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub account

### **Step 2: Deploy with Blueprint (Recommended)**
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Select repository: `Medical-Text-Classification`
4. Click **"Apply"**
5. Wait for services to be created

### **Step 3: Configure Secrets**
1. Go to **medtext-api** service
2. Click **"Environment"** tab
3. Update these variables:
   - `SECRET_KEY`: Copy the value above
   - `API_KEYS`: Copy the value above
4. Click **"Save Changes"**

### **Step 4: Wait for Deployment**
- Database: ~2-3 minutes
- API: ~5-10 minutes
- Frontend: ~3-5 minutes

---

## 🔍 **Post-Deployment Verification**

### **Test URLs** (replace with your actual URLs):
- **Health Check**: `https://medtext-api.onrender.com/health`
- **Frontend**: `https://medtext-frontend.onrender.com`
- **API Docs**: `https://medtext-api.onrender.com/docs`

### **Verification Steps**:
1. [ ] Health endpoint returns 200 OK
2. [ ] Frontend loads without errors
3. [ ] API documentation is accessible
4. [ ] Can make a test prediction
5. [ ] No errors in Render logs

### **Test Prediction**:
```bash
curl -X POST "https://medtext-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: T3z3cJCQ78KeX_IGqit64tbrJxZzF5TKGSsIdn1me3Y" \
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

---

## 🚨 **Troubleshooting**

### **Common Issues**:

#### **Build Fails**
- Check that model files are committed to GitHub
- Verify Dockerfile syntax
- Check build logs in Render dashboard

#### **Model Not Loading**
- Ensure all files in `models/biomedbert_model/` are present
- Check file sizes (Render has limits)
- Verify model path configuration

#### **CORS Errors**
- Update `ALLOWED_ORIGINS` in API environment variables
- Use exact frontend URL: `https://medtext-frontend.onrender.com`

#### **Database Connection**
- Verify `DATABASE_URL` is auto-populated
- Check database service is running
- Ensure same region for database and API

---

## 💰 **Cost Summary**

**Monthly costs:**
- PostgreSQL Starter: $7/month
- API Standard Plan: $25/month
- Frontend Static Site: FREE
- **Total: ~$32/month**

**Cost optimization:**
- Start with Starter plans
- Monitor usage and scale as needed
- Consider annual billing for discounts

---

## 🎉 **Success Indicators**

When deployment is successful, you'll have:

✅ **Working URLs:**
- Frontend: `https://medtext-frontend.onrender.com`
- API: `https://medtext-api.onrender.com`
- Docs: `https://medtext-api.onrender.com/docs`

✅ **Functional Features:**
- Medical text classification
- Real-time predictions
- Secure API with authentication
- Responsive web interface
- Health monitoring
- Automatic scaling

✅ **Production Ready:**
- SSL certificates
- Security headers
- Rate limiting
- Error handling
- Logging and monitoring

---

## 📞 **Need Help?**

- **Render Support**: [help.render.com](https://help.render.com)
- **Documentation**: See `RENDER_DEPLOYMENT_SIMPLE.md`
- **Detailed Guide**: See `docs/RENDER_DEPLOYMENT.md`

---

**🎊 Your Medical Text Classification app will be live on the internet!**

**Share your app:**
- Frontend URL: `https://medtext-frontend.onrender.com`
- API for developers: `https://medtext-api.onrender.com/docs`
