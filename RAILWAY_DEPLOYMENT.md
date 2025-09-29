# 🚀 Railway Deployment Guide

This guide will help you deploy the Google Maps Scraper to Railway for team access.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Node.js**: Install Node.js for Railway CLI
3. **Git**: For version control

## 🛠️ Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Run the deployment script
python deploy_railway.py
```

### Option 2: Manual Deployment

#### Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version
```

#### Step 2: Login to Railway

```bash
# Login to Railway
railway login
```

#### Step 3: Initialize Project

```bash
# Initialize Railway project
railway init

# This will create a railway.json file
```

#### Step 4: Deploy

```bash
# Deploy to Railway
railway up
```

## 🔧 Configuration

### Environment Variables

Railway will automatically set these environment variables:

- `PORT=8000` - Port for the web interface
- `PYTHONUNBUFFERED=1` - Python output buffering
- `DISPLAY=:99` - X11 display for headless Chrome
- `CHROME_BIN=/usr/bin/google-chrome` - Chrome binary path
- `CHROME_PATH=/usr/bin/google-chrome` - Chrome path
- `OUTPUT_PATH=/app/output` - Output directory
- `HEADLESS_MODE=1` - Force headless mode
- `RAILWAY_ENVIRONMENT=production` - Environment flag
- `DEBUG=false` - Debug mode

### Custom Configuration

You can modify environment variables in Railway dashboard:

1. Go to your project dashboard
2. Click on "Variables" tab
3. Add or modify environment variables

## 🌐 Accessing Your App

After deployment, Railway will provide you with a URL like:
```
https://your-app-name.railway.app
```

### Web Interface Features

- **Modern UI**: Clean, responsive web interface
- **Real-time Updates**: Live progress during scraping
- **File Downloads**: Automatic file download after completion
- **Job Management**: Track scraping jobs
- **Health Monitoring**: Built-in health checks

## 📊 Monitoring and Logs

### View Logs

```bash
# View real-time logs
railway logs

# View logs with timestamps
railway logs --timestamps
```

### Monitor Performance

```bash
# Check app status
railway status

# View metrics
railway metrics
```

## 🔄 Updates and Maintenance

### Update Your App

```bash
# Make changes to your code
git add .
git commit -m "Update scraper"

# Deploy updates
railway up
```

### Rollback Deployment

```bash
# View deployment history
railway deployments

# Rollback to previous version
railway rollback <deployment-id>
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Chrome Issues
```bash
# Check if Chrome is installed
railway run python -c "import subprocess; print(subprocess.run(['google-chrome', '--version'], capture_output=True).stdout.decode())"
```

#### 2. Memory Issues
- Railway has memory limits
- Monitor memory usage in dashboard
- Consider upgrading plan if needed

#### 3. Timeout Issues
- Scraping jobs have time limits
- Break large scraping tasks into smaller chunks
- Use pagination for large datasets

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug mode
railway variables set DEBUG=true

# Redeploy
railway up
```

## 💰 Railway Pricing

### Free Tier
- 500 hours/month
- 1GB RAM
- Perfect for small teams

### Pro Tier
- $5/month per developer
- 8GB RAM
- Better for production use

## 🔒 Security Considerations

### Environment Variables
- Never commit sensitive data
- Use Railway's environment variables
- Rotate API keys regularly

### Access Control
- Limit team access
- Use Railway's team features
- Monitor usage

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale to multiple instances
railway scale web=3
```

### Vertical Scaling
- Upgrade Railway plan
- Increase memory allocation
- Optimize Chrome settings

## 🎯 Best Practices

### 1. Resource Management
- Monitor memory usage
- Use headless mode
- Optimize Chrome settings

### 2. Error Handling
- Implement proper error handling
- Use try-catch blocks
- Log errors properly

### 3. Performance
- Use connection pooling
- Implement caching
- Optimize database queries

## 📞 Support

### Railway Support
- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub](https://github.com/railwayapp)

### Project Support
- Check project README
- Review error logs
- Test locally first

## 🎉 Success!

Once deployed, your team can:

1. **Access the web interface** at your Railway URL
2. **Start scraping jobs** through the web UI
3. **Download results** automatically
4. **Monitor progress** in real-time
5. **Share access** with team members

### Team Onboarding

1. Share the Railway URL with your team
2. Provide basic usage instructions
3. Set up monitoring and alerts
4. Train team on best practices

---

**Note**: This deployment is optimized for Railway's environment. The scraper runs in headless mode and is designed for cloud deployment.
