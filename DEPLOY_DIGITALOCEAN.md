# 🚀 DigitalOcean Deployment Guide

## Why DigitalOcean?
- ✅ **No Consent Page Issues**: Full control over Chrome installation
- ✅ **Proven for Scrapers**: Many successful scraping projects
- ✅ **Affordable**: $5/month for basic droplet
- ✅ **Full Control**: Install any Chrome version you need
- ✅ **Reliable**: 99.99% uptime SLAx`

## 📋 Prerequisites
- DigitalOcean account (FREE with $200 credit)
- Domain name (optional)
- SSH client (PuTTY on Windows, Terminal on Mac/Linux)

## 🎁 **FREE TRIAL - $200 Credit!**

DigitalOcean gives **$200 free credit** to new users, which means you can test for **40+ days** without paying anything!

### How to Get Free Credit:
1. **Sign up**: [digitalocean.com](https://digitalocean.com)
2. **Add payment method**: Required for verification (but you won't be charged)
3. **Get $200 credit**: Automatically added to your account
4. **Test for free**: $5/month droplet = 40 days free!

## 🚀 Step 1: Create Droplet

1. **Login to DigitalOcean**
2. **Click "Create" → "Droplets"**
3. **Choose Configuration:**
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic $5/month (1GB RAM, 1 CPU)
   - **Authentication**: SSH Key (recommended) or Password
   - **Hostname**: `google-maps-scraper`
   - **Region**: Choose closest to your users

## 🚀 Step 2: Server Setup

### Connect to Your Droplet
```bash


```

### Update System
```bash
apt update && apt upgrade -y
```

### Install Python and Dependencies
```bash
# Install Python 3.9+
apt install python3 python3-pip python3-venv -y

# Install system dependencies for Chrome
apt install -y wget gnupg unzip curl xvfb fonts-liberation libasound2 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libnss3 libx11-xcb1 libxcb-dri3-0 libxtst6 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf-2.0-0 -y
```

### Install Google Chrome
```bash
# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
apt update
apt install google-chrome-stable -y

# Verify installation
google-chrome --version
```

## 🚀 Step 3: Deploy Your Application

### Clone Your Repository
```bash
# Install Git
apt install git -y

# Clone your repository
git clone https://github.com/dev-omena/scrapper-v2.git
cd scrapper-v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Create Production App
```bash
# Create production version
cat > app/production_app.py << 'EOF'
from flask import Flask, render_template_string, request, jsonify, send_file
import os
import threading
import time
from datetime import datetime
from scraper.improved_scraper import ImprovedBackend as Backend
from scraper.communicator import Communicator

app = Flask(__name__)

# Global variables for job tracking
current_job = None
job_status = {"status": "idle", "message": "Ready to scrape", "progress": 0}
available_files = []

class ProductionFrontend:
    def show_message(self, message):
        global job_status
        job_status["message"] = message
        print(f"Production: {message}")

class ProductionBackend:
    def show_message(self, message):
        global job_status
        job_status["message"] = message
        print(f"Production: {message}")

def run_scraper(query, headless_mode=True):
    global current_job, job_status, available_files
    
    try:
        job_status = {"status": "running", "message": f"Starting scraping job", "progress": 0}
        
        # Set up communicator
        Communicator.set_frontend_object(ProductionFrontend())
        Communicator.set_backend_object(ProductionBackend())
        
        # Initialize scraper
        scraper = Backend(healdessmode=headless_mode)
        
        # Run scraping
        scraper.main(query)
        
        # Update status
        job_status = {"status": "completed", "message": "Scraping completed successfully!", "progress": 100}
        
        # Update available files
        output_dir = "output"
        if os.path.exists(output_dir):
            available_files = [f for f in os.listdir(output_dir) if f.endswith(('.xlsx', '.csv', '.json'))]
        
    except Exception as e:
        job_status = {"status": "error", "message": f"Error: {str(e)}", "progress": 0}
        print(f"Scraping error: {str(e)}")
    finally:
        current_job = None

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Maps Scraper - Production</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .status.running { background: #fff3cd; border: 1px solid #ffeaa7; }
        .status.completed { background: #d4edda; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; border: 1px solid #f5c6cb; }
        .files { margin-top: 20px; }
        .file-item { background: white; padding: 10px; margin: 5px 0; border-radius: 5px; border: 1px solid #ddd; }
        .download-btn { background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ Google Maps Scraper - Production</h1>
        <p>Scrape business data from Google Maps with ease!</p>
        
        <form id="scrapeForm">
            <div class="form-group">
                <label for="query">Search Query:</label>
                <input type="text" id="query" name="query" placeholder="e.g., restaurants in New York" required>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="headless" checked> Run in headless mode (recommended for server)
                </label>
            </div>
            <button type="submit" id="submitBtn">Start Scraping</button>
        </form>
        
        <div id="status" class="status" style="display: none;">
            <h3>Status:</h3>
            <p id="statusMessage">Ready to scrape</p>
        </div>
        
        <div id="files" class="files" style="display: none;">
            <h3>📁 Available Files:</h3>
            <div id="filesList"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('scrapeForm');
        const submitBtn = document.getElementById('submitBtn');
        const statusDiv = document.getElementById('status');
        const statusMessage = document.getElementById('statusMessage');
        const filesDiv = document.getElementById('files');
        const filesList = document.getElementById('filesList');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const headless = document.getElementById('headless').checked;
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Scraping...';
            
            statusDiv.style.display = 'block';
            statusDiv.className = 'status running';
            statusMessage.textContent = 'Starting scraping job...';
            
            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, headless: headless})
                });
                
                if (response.ok) {
                    // Start polling for status
                    pollStatus();
                } else {
                    throw new Error('Scraping failed to start');
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusMessage.textContent = 'Error: ' + error.message;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Scraping';
            }
        });

        async function pollStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                statusMessage.textContent = data.message;
                
                if (data.status === 'running') {
                    setTimeout(pollStatus, 2000);
                } else if (data.status === 'completed') {
                    statusDiv.className = 'status completed';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Start Scraping';
                    loadFiles();
                } else if (data.status === 'error') {
                    statusDiv.className = 'status error';
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Start Scraping';
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusMessage.textContent = 'Error checking status: ' + error.message;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Scraping';
            }
        }

        async function loadFiles() {
            try {
                const response = await fetch('/files');
                const files = await response.json();
                
                if (files.length > 0) {
                    filesDiv.style.display = 'block';
                    filesList.innerHTML = files.map(file => `
                        <div class="file-item">
                            <strong>${file}</strong>
                            <a href="/download/${file}" class="download-btn">Download</a>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading files:', error);
            }
        }

        // Load files on page load
        loadFiles();
    </script>
</body>
</html>
    ''')

@app.route('/scrape', methods=['POST'])
def scrape():
    global current_job
    
    if current_job and current_job.is_alive():
        return jsonify({"error": "Another scraping job is already running"}), 400
    
    data = request.get_json()
    query = data.get('query', '')
    headless = data.get('headless', True)
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    # Start scraping in background thread
    current_job = threading.Thread(target=run_scraper, args=(query, headless))
    current_job.start()
    
    return jsonify({"message": "Scraping started", "query": query})

@app.route('/status')
def status():
    return jsonify(job_status)

@app.route('/files')
def files():
    output_dir = "output"
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith(('.xlsx', '.csv', '.json'))]
        return jsonify(files)
    return jsonify([])

@app.route('/download/<filename>')
def download_file(filename):
    output_dir = "output"
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
```

### Create Systemd Service
```bash
# Create systemd service file
cat > /etc/systemd/system/maps-scraper.service << 'EOF'
[Unit]
Description=Google Maps Scraper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/scrapper-v2
Environment=PATH=/root/scrapper-v2/venv/bin
ExecStart=/root/scrapper-v2/venv/bin/python app/production_app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable maps-scraper
systemctl start maps-scraper
systemctl status maps-scraper
```

## 🚀 Step 4: Configure Firewall

```bash
# Allow HTTP traffic
ufw allow 5000
ufw allow ssh
ufw --force enable
```

## 🚀 Step 5: Test Your Deployment

1. **Open your browser**: `http://YOUR_DROPLET_IP:5000`
2. **Test scraping**: Try "restaurants in New York"
3. **Check logs**: `journalctl -u maps-scraper -f`

## 🚀 Step 6: Domain Setup (Optional)

### Install Nginx
```bash
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

### Configure Nginx
```bash
cat > /etc/nginx/sites-available/maps-scraper << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/maps-scraper /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## 🚀 Step 7: SSL Certificate (Optional)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d YOUR_DOMAIN.com
```

## 📊 **Expected Results**

✅ **No Consent Page Issues**: Full Chrome control  
✅ **Real Scraping**: Actual Google Maps data  
✅ **Reliable Performance**: 99.99% uptime  
✅ **Cost Effective**: $5/month  
✅ **Full Control**: Install any Chrome version  

## 🔧 **Troubleshooting**

### Check Service Status
```bash
systemctl status maps-scraper
journalctl -u maps-scraper -f
```

### Restart Service
```bash
systemctl restart maps-scraper
```

### Check Chrome Installation
```bash
google-chrome --version
which google-chrome
```

### Test Chrome Headless
```bash
google-chrome --headless --disable-gpu --dump-dom https://www.google.com
```

## 💰 **Cost Breakdown**

### **FREE TRIAL (First 40+ Days)**
- **DigitalOcean Droplet**: $0 (using $200 free credit)
- **Domain (optional)**: $0 (not required for testing)
- **Total**: $0 for 40+ days!

### **After Free Trial**
- **DigitalOcean Droplet**: $5/month
- **Domain (optional)**: $10-15/year
- **Total**: ~$6/month

## 🎯 **Why This Will Work**

1. **Full Chrome Control**: Install exact Chrome version you need
2. **No Platform Restrictions**: Railway's limitations don't apply
3. **Proven Solution**: Many successful scraping projects use this setup
4. **Cost Effective**: Much cheaper than Railway Pro
5. **Reliable**: 99.99% uptime SLA

This setup should completely solve your consent page issues! 🚀
