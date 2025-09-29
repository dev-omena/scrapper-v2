#!/usr/bin/env python3
"""
Railway deployment script for Google Maps Scraper
This script helps set up and deploy the scraper to Railway
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        # Try npm first
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try yarn
            subprocess.run(['yarn', 'global', 'add', '@railway/cli'], check=True)
            print("✅ Railway CLI installed via yarn")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Railway CLI")
            print("Please install manually: npm install -g @railway/cli")
            return False

def create_railway_config():
    """Create Railway configuration files"""
    print("📝 Creating Railway configuration...")
    
    # Create Procfile for Railway
    procfile_content = "web: python app/railway_app.py"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Created Procfile")
    
    # Create .railwayignore
    ignore_content = """# Railway ignore file
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.DS_Store
.vscode/
.idea/
*.swp
*.swo
*~
"""
    with open(".railwayignore", "w") as f:
        f.write(ignore_content)
    print("✅ Created .railwayignore")

def setup_environment():
    """Setup environment for Railway deployment"""
    print("🔧 Setting up environment...")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    print("✅ Created output directory")
    
    # Check if all required files exist
    required_files = [
        "app/railway_app.py",
        "Dockerfile",
        "railway.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    try:
        # Login to Railway
        print("🔐 Logging in to Railway...")
        subprocess.run(['railway', 'login'], check=True)
        
        # Initialize project
        print("📁 Initializing Railway project...")
        subprocess.run(['railway', 'init'], check=True)
        
        # Set environment variables
        print("⚙️ Setting environment variables...")
        env_vars = {
            'PORT': '8000',
            'PYTHONUNBUFFERED': '1',
            'DISPLAY': ':99',
            'CHROME_BIN': '/usr/bin/google-chrome',
            'CHROME_PATH': '/usr/bin/google-chrome',
            'OUTPUT_PATH': '/app/output',
            'HEADLESS_MODE': '1',
            'RAILWAY_ENVIRONMENT': 'production',
            'DEBUG': 'false'
        }
        
        for key, value in env_vars.items():
            subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
        
        # Deploy
        print("🚀 Deploying application...")
        subprocess.run(['railway', 'up'], check=True)
        
        print("✅ Deployment successful!")
        print("🌐 Your application is now live on Railway!")
        
        # Get the URL
        try:
            result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
            if result.returncode == 0:
                domain = result.stdout.strip()
                print(f"🔗 Access your app at: https://{domain}")
        except:
            print("🔗 Check Railway dashboard for your app URL")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Railway Deployment Setup for Google Maps Scraper")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app/run.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Create Railway config
    create_railway_config()
    
    # Check Railway CLI
    if not check_railway_cli():
        print("📦 Railway CLI not found. Installing...")
        if not install_railway_cli():
            print("❌ Please install Railway CLI manually:")
            print("   npm install -g @railway/cli")
            sys.exit(1)
    
    # Deploy to Railway
    if deploy_to_railway():
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Check your Railway dashboard for the app URL")
        print("2. Test the web interface")
        print("3. Share the URL with your team")
        print("\n💡 Tips:")
        print("- The app runs in headless mode on Railway")
        print("- All scraping operations are performed in the background")
        print("- Files are automatically downloaded after scraping")
    else:
        print("❌ Deployment failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
