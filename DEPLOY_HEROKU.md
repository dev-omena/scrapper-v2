# 🚀 Heroku Deployment Guide

## Why Heroku?
- ✅ **Better Chrome Support**: Less restrictive than Railway
- ✅ **Proven for Scrapers**: Many successful scraping projects
- ✅ **Easy Deployment**: Simple git push deployment
- ✅ **Add-ons Available**: Chrome buildpack support
- ✅ **Reliable**: 99.9% uptime

## 📋 Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git repository

## 🚀 Step 1: Install Heroku CLI

### Windows
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
# Or use chocolatey
choco install heroku-cli
```

### Mac
```bash
brew install heroku/brew/heroku
```

### Linux
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

## 🚀 Step 2: Login to Heroku

```bash
heroku login
```

## 🚀 Step 3: Create Heroku App

```bash
# Create app
heroku create your-maps-scraper

# Add Chrome buildpack
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-chromedriver
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
```

## 🚀 Step 4: Create Heroku-Specific Files

### Create `Procfile`
```bash
cat > Procfile << 'EOF'
web: python app/heroku_app.py
EOF
```

### Create `app/heroku_app.py`
```bash
cat > app/heroku_app.py << 'EOF'
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

class HerokuFrontend:
    def show_message(self, message):
        global job_status
        job_status["message"] = message
        print(f"Heroku: {message}")

class HerokuBackend:
    def show_message(self, message):
        global job_status
        job_status["message"] = message
        print(f"Heroku: {message}")

def run_scraper(query, headless_mode=True):
    global current_job, job_status, available_files
    
    try:
        job_status = {"status": "running", "message": f"Starting scraping job", "progress": 0}
        
        # Set up communicator
        Communicator.set_frontend_object(HerokuFrontend())
        Communicator.set_backend_object(HerokuBackend())
        
        # Initialize scraper with Heroku-specific settings
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
    <title>Google Maps Scraper - Heroku</title>
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
        <h1>🗺️ Google Maps Scraper - Heroku</h1>
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
    
    # Get port from environment (Heroku sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
EOF
```

## 🚀 Step 5: Configure Environment Variables

```bash
# Set environment variables
heroku config:set CHROME_BIN=/app/.chrome-for-testing/chrome-linux64/chrome
heroku config:set CHROME_PATH=/app/.chrome-for-testing/chrome-linux64/chrome
heroku config:set DISPLAY=:99
heroku config:set PYTHONUNBUFFERED=1
```

## 🚀 Step 6: Deploy to Heroku

```bash
# Add and commit files
git add .
git commit -m "Add Heroku deployment files"

# Deploy to Heroku
git push heroku master
```

## 🚀 Step 7: Test Your Deployment

```bash
# Open your app
heroku open

# Check logs
heroku logs --tail
```

## 🚀 Step 8: Scale Your App (Optional)

```bash
# Scale to 1 dyno (free tier allows 1 dyno)
heroku ps:scale web=1

# For production, you might want to scale up
heroku ps:scale web=2
```

## 📊 **Expected Results**

✅ **Better Chrome Support**: Heroku's Chrome buildpack is more reliable  
✅ **No Consent Page Issues**: Better Chrome configuration  
✅ **Real Scraping**: Actual Google Maps data  
✅ **Easy Deployment**: Simple git push  
✅ **Free Tier Available**: $0/month for basic usage  

## 🔧 **Troubleshooting**

### Check App Status
```bash
heroku ps
heroku logs --tail
```

### Restart App
```bash
heroku restart
```

### Check Chrome Installation
```bash
heroku run google-chrome --version
```

### Test Chrome Headless
```bash
heroku run google-chrome --headless --disable-gpu --dump-dom https://www.google.com
```

## 💰 **Cost Breakdown**

- **Heroku Free Tier**: $0/month (limited hours)
- **Heroku Basic**: $7/month (unlimited hours)
- **Total**: $0-7/month

## 🎯 **Why This Will Work**

1. **Better Chrome Buildpack**: Heroku's Chrome support is more mature
2. **Less Restrictive**: No Railway-style limitations
3. **Proven Solution**: Many successful scraping projects use Heroku
4. **Easy Deployment**: Simple git push deployment
5. **Free Tier**: Test for free before upgrading

This should solve your consent page issues! 🚀
