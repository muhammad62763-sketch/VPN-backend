# 🚀 Vercel Deployment Guide - VPN Backend API

**Last Updated:** 2026-03-08  
**Status:** Production Ready  
**Platform:** Vercel Serverless

---

## ⚠️ CRITICAL: Pre-Deployment Checklist

Before deploying to Vercel, ensure:

- [x] Database migration completed (`python apply_complete_schema_fix.py`)
- [x] All secrets rotated (never use example secrets)
- [x] `.env` file configured with production values
- [x] Security scan passed (`bandit -r app/`)
- [x] Code diagnostics passed
- [ ] Vercel account created
- [ ] Vercel CLI installed
- [ ] Environment variables configured in Vercel dashboard

---

## 📋 Step-by-Step Deployment

### Step 1: Install Vercel CLI

```bash
# Install globally
npm install -g vercel

# Or use npx (no installation needed)
npx vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

Choose your login method:
- GitHub
- GitLab
- Bitbucket
- Email

### Step 3: Configure Environment Variables

**IMPORTANT:** Set these in Vercel Dashboard (NOT in code)

Go to: **Project Settings → Environment Variables**

Add the following variables:

```env
# Database
NEON_DATABASE_URL=postgresql://username:password@host.region.aws.neon.tech/dbname?sslmode=require

# JWT (Generate new secrets!)
JWT_SECRET_KEY=<your_64_byte_hex_secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin
ADMIN_REGISTRATION_SECRET=<your_64_byte_hex_secret>
ADMIN_IP_WHITELIST=[]

# App
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
ENVIRONMENT=production

# Security
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=900
SESSION_TIMEOUT=3600
REQUIRE_2FA_FOR_ADMIN=true

# VPN
WG_SERVER_PUBLIC_KEY=<your_wireguard_public_key>
WG_SERVER_ENDPOINT=<your_vps_ip>:51820
WG_DNS=1.1.1.1
MAX_DEVICES_PER_USER=5
DEFAULT_BANDWIDTH_LIMIT=107374182400

# Signing
ED25519_PRIVATE_KEY_HEX=<your_32_byte_hex_secret>

# Monitoring
ENABLE_METRICS=true
ENABLE_AUDIT_LOGGING=true
```

**How to add in Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable one by one
5. Select environments: Production, Preview, Development

### Step 4: Deploy to Vercel

#### Option A: Deploy via CLI (Recommended)

```bash
# Navigate to project directory
cd D:\AI\VPN\backend

# Deploy to production
vercel --prod

# Or deploy to preview first
vercel
```

#### Option B: Deploy via Git Integration

1. Push code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/new
3. Import your repository
4. Vercel will auto-detect the configuration
5. Click "Deploy"

### Step 5: Verify Deployment

After deployment, Vercel will provide a URL like:
```
https://your-project-name.vercel.app
```

Test the deployment:

```bash
# Test health endpoint
curl https://your-project-name.vercel.app/api/v1/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

---

## 🔧 Vercel Configuration Files

### vercel.json (Already Configured)

```json
{
    "version": 2,
    "builds": [
        {
            "src": "api/index.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "api/index.py"
        }
    ],
    "env": {
        "PYTHONPATH": "."
    }
}
```

### .vercelignore (Create this file)

```
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.env.local
.git/
.gitignore
*.md
tests/
.pytest_cache/
.coverage
htmlcov/
```

---

## 🌐 Custom Domain Setup

### Add Custom Domain

1. Go to Project Settings → Domains
2. Click "Add Domain"
3. Enter your domain: `api.yourdomain.com`
4. Follow DNS configuration instructions

### DNS Configuration

Add these records to your DNS provider:

**For apex domain (yourdomain.com):**
```
Type: A
Name: @
Value: 76.76.21.21
```

**For subdomain (api.yourdomain.com):**
```
Type: CNAME
Name: api
Value: cname.vercel-dns.com
```

### SSL Certificate

Vercel automatically provisions SSL certificates via Let's Encrypt.
- No configuration needed
- Auto-renewal
- HTTPS enforced

---

## 📊 Monitoring & Logs

### View Deployment Logs

```bash
# View logs in real-time
vercel logs --follow

# View logs for specific deployment
vercel logs <deployment-url>
```

### Vercel Dashboard

Access logs at:
```
https://vercel.com/your-username/your-project/deployments
```

Features:
- Real-time logs
- Function invocations
- Error tracking
- Performance metrics

---

## 🔄 Continuous Deployment

### Automatic Deployments

When connected to Git:
- **Push to main/master** → Production deployment
- **Push to other branches** → Preview deployment
- **Pull requests** → Preview deployment with unique URL

### Manual Deployments

```bash
# Deploy current directory
vercel

# Deploy specific branch
vercel --prod

# Deploy with custom name
vercel --name my-vpn-api
```

---

## ⚙️ Advanced Configuration

### Environment-Specific Settings

```json
{
  "env": {
    "PYTHONPATH": "."
  },
  "build": {
    "env": {
      "PYTHON_VERSION": "3.11"
    }
  }
}
```

### Function Configuration

```json
{
  "functions": {
    "api/index.py": {
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

### Headers Configuration

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://your-frontend.com"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        }
      ]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
- Ensure `PYTHONPATH` is set in `vercel.json`
- Check `api/index.py` imports correctly

#### Issue 2: Database Connection Failed
**Error:** `Connection refused` or `SSL required`

**Solution:**
- Verify `NEON_DATABASE_URL` in environment variables
- Ensure URL includes `?sslmode=require`
- Check database is accessible from Vercel IPs

#### Issue 3: Environment Variables Not Loading
**Error:** `KeyError: 'JWT_SECRET_KEY'`

**Solution:**
- Add variables in Vercel Dashboard
- Redeploy after adding variables
- Check variable names match exactly

#### Issue 4: Function Timeout
**Error:** `Function execution timed out`

**Solution:**
- Optimize database queries
- Increase timeout in `vercel.json`:
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

#### Issue 5: Cold Start Issues
**Symptom:** First request is slow

**Solution:**
- Use Vercel Pro for faster cold starts
- Implement connection pooling
- Cache frequently accessed data

---

## 📈 Performance Optimization

### Database Connection Pooling

Already configured in `app/services/db.py`:
```python
_pool = await asyncpg.create_pool(
    dsn=url,
    min_size=1,
    max_size=5,  # Vercel serverless: keep pool small
    ssl="require",
    command_timeout=10,
)
```

### Caching Strategy

Add caching headers:
```json
{
  "headers": [
    {
      "source": "/api/v1/vpn/servers",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=300"
        }
      ]
    }
  ]
}
```

### Edge Functions (Optional)

For better performance, consider Vercel Edge Functions:
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "edge"
    }
  }
}
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
- ✅ Never commit secrets to Git
- ✅ Use Vercel Dashboard for secrets
- ✅ Rotate secrets regularly
- ✅ Use different secrets for preview/production

### 2. CORS Configuration
- ✅ Whitelist specific origins
- ✅ Don't use `*` in production
- ✅ Configure in `app/main.py`

### 3. Rate Limiting
- ✅ Already configured in middleware
- ✅ Monitor for abuse
- ✅ Adjust limits as needed

### 4. HTTPS Only
- ✅ Vercel enforces HTTPS
- ✅ HSTS headers configured
- ✅ Redirect HTTP to HTTPS

---

## 💰 Pricing Considerations

### Vercel Free Tier
- 100 GB bandwidth/month
- 100 hours serverless function execution
- Unlimited deployments
- Automatic HTTPS

### Vercel Pro ($20/month)
- 1 TB bandwidth
- 1000 hours execution
- Faster cold starts
- Advanced analytics
- Password protection

### Vercel Enterprise
- Custom pricing
- Dedicated support
- SLA guarantees
- Advanced security

**Recommendation:** Start with Free tier, upgrade to Pro when needed.

---

## 📞 Support & Resources

### Vercel Documentation
- https://vercel.com/docs
- https://vercel.com/docs/functions/serverless-functions/runtimes/python

### Community
- Vercel Discord: https://vercel.com/discord
- GitHub Discussions: https://github.com/vercel/vercel/discussions

### Status Page
- https://www.vercel-status.com/

---

## ✅ Post-Deployment Checklist

After successful deployment:

- [ ] Test all API endpoints
- [ ] Verify database connectivity
- [ ] Test authentication flow
- [ ] Test VPN config generation
- [ ] Check error logging
- [ ] Monitor performance
- [ ] Set up alerts
- [ ] Document API URL
- [ ] Update frontend API URL
- [ ] Test from mobile app
- [ ] Monitor for 24 hours
- [ ] Set up backup strategy

---

## 🚀 Quick Deploy Commands

```bash
# First time deployment
vercel

# Production deployment
vercel --prod

# View logs
vercel logs --follow

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-url>

# Check project info
vercel inspect

# Pull environment variables
vercel env pull
```

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ Health endpoint returns 200 OK
✅ Authentication works
✅ Database queries execute
✅ No errors in logs
✅ Response times < 1 second
✅ SSL certificate active
✅ Custom domain working (if configured)
✅ CORS configured correctly
✅ Rate limiting active
✅ Security headers present

---

## 📝 Deployment Log Template

Keep track of deployments:

```
Deployment Date: 2026-03-08
Deployment URL: https://vpn-backend-xyz.vercel.app
Git Commit: abc123def
Environment: Production
Status: Success
Response Time: 250ms
Issues: None
Notes: Initial production deployment
```

---

**Deployment Guide Version:** 1.0  
**Last Updated:** 2026-03-08  
**Maintained By:** DevOps Team
