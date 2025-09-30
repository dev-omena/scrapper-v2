"""
Railway Flask Web Application for Google Maps Scraper
Optimized for Railway deployment with headless Chrome
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import threading
import time
import uuid
import json
from datetime import datetime
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.improved_scraper import ImprovedBackend as Backend
from scraper.communicator import Communicator
from scraper.datasaver import DataSaver

app = Flask(__name__)

class RailwayCommunicator:
    """Custom communicator for Railway web interface"""
    def __init__(self):
        self.messages = []
        self.status = "ready"
        self.job_id = None
        self.scraped_data = []
        self.output_file = None
    
    def show_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {message}")
        print(f"Railway: {message}")
    
    def show_error_message(self, message, error_code):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] ERROR: {message} (Code: {error_code})")
        print(f"Railway ERROR: {message}")
    
    def end_processing(self):
        self.status = "completed"
    
    def get_output_format(self):
        return getattr(self, 'output_format', 'excel')
    
    def get_search_query(self):
        return getattr(self, 'search_query', 'unknown')

# Global communicator instance
railway_comm = RailwayCommunicator()

@app.route('/')
def index():
    """Main web interface"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Google Maps Scraper - Railway</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 1.1em;
            }
            
            input, select {
                width: 100%;
                padding: 15px;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #4CAF50;
            }
            
            .checkbox-group {
                display: flex;
                align-items: center;
                margin: 20px 0;
            }
            
            .checkbox-group input[type="checkbox"] {
                width: auto;
                margin-right: 10px;
            }
            
            button {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 18px;
                font-weight: 600;
                transition: transform 0.2s;
                width: 100%;
            }
            
            button:hover:not(:disabled) {
                transform: translateY(-2px);
            }
            
            button:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
            }
            
            .status-section {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #4CAF50;
            }
            
            .status {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .status.ready { color: #4CAF50; }
            .status.running { color: #2196F3; }
            .status.completed { color: #4CAF50; }
            .status.error { color: #f44336; }
            
            .messages {
                max-height: 300px;
                overflow-y: auto;
                background: #2c3e50;
                color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .message {
                margin-bottom: 5px;
                padding: 2px 0;
            }
            
            .message.error { color: #e74c3c; }
            .message.success { color: #2ecc71; }
            .message.info { color: #3498db; }
            
            .download-section {
                margin-top: 20px;
                padding: 15px;
                background: #e8f5e8;
                border-radius: 8px;
                text-align: center;
                display: none;
            }
            
            .download-btn {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin: 5px;
            }
            
            .download-btn:hover {
                background: #1976D2;
            }
            
            .info-box {
                background: #e3f2fd;
                border: 1px solid #2196F3;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .info-box h3 {
                color: #1976D2;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗺️ Google Maps Scraper</h1>
                <p>Deployed on Railway - Team Access Portal</p>
                <p style="font-size: 0.8em; opacity: 0.7;">Version: v2.1.3 - Debug Enhanced</p>
            </div>
            
            <div class="content">
                <div class="info-box">
                    <h3>ℹ️ Railway Deployment Info</h3>
                    <p>This scraper runs in headless mode on Railway. All scraping operations are performed in the background without a visible browser window.</p>
                </div>
                
                <form id="scrapeForm">
                    <div class="form-group">
                        <label for="search_query">Search Query:</label>
                        <input type="text" id="search_query" name="search_query" 
                               placeholder="e.g., restaurants in New York, coffee shops in London" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="output_format">Output Format:</label>
                        <select id="output_format" name="output_format">
                            <option value="excel">Excel (.xlsx)</option>
                            <option value="csv">CSV (.csv)</option>
                            <option value="json">JSON (.json)</option>
                        </select>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="headless_mode" name="headless_mode" checked disabled>
                        <label for="headless_mode">Headless Mode (Required for Railway)</label>
                    </div>
                    
                    <button type="submit" id="submitBtn">Start Scraping</button>
                </form>
                
                <div class="status-section">
                    <div class="status" id="status">Ready</div>
                    <div id="messages" class="messages"></div>
                </div>
                
                <div class="download-section" id="downloadSection">
                    <h3>📁 Download Results</h3>
                    <p>Your scraping is complete! Download the results:</p>
                    <a href="#" id="downloadLink" class="download-btn">Download File</a>
                </div>
            </div>
        </div>

        <script>
            const form = document.getElementById('scrapeForm');
            const submitBtn = document.getElementById('submitBtn');
            const status = document.getElementById('status');
            const messages = document.getElementById('messages');
            const downloadSection = document.getElementById('downloadSection');
            const downloadLink = document.getElementById('downloadLink');
            
            let currentJobId = null;
            let pollInterval = null;
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = {
                    search_query: formData.get('search_query'),
                    output_format: formData.get('output_format'),
                    healdessmode: 1  // Always headless on Railway (note: typo in original code)
                };
                
                submitBtn.disabled = true;
                status.textContent = 'Starting...';
                status.className = 'status running';
                downloadSection.style.display = 'none';
                
                try {
                    const response = await fetch('/scrape', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    console.log(result);
                    
                    if (result.status === 'started') {
                        currentJobId = result.job_id;
                        status.textContent = 'Scraping in progress...';
                        status.className = 'status running';
                        pollStatus();
                    } else {
                        status.textContent = 'Error starting scraping';
                        status.className = 'status error';
                        submitBtn.disabled = false;
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    status.textContent = 'Error starting scraping';
                    status.className = 'status error';
                    submitBtn.disabled = false;
                }
            });
            
            function pollStatus() {
                if (pollInterval) clearInterval(pollInterval);
                
                pollInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
                        status.textContent = data.status;
                        status.className = `status ${data.status}`;
                        
                        // Update messages
                        messages.innerHTML = data.messages.map(msg => {
                            let className = 'message';
                            if (msg.includes('ERROR')) className += ' error';
                            else if (msg.includes('completed') || msg.includes('success')) className += ' success';
                            else className += ' info';
                            
                            return `<div class="${className}">${msg}</div>`;
                        }).join('');
                        
                        messages.scrollTop = messages.scrollHeight;
                        
                        if (data.status === 'completed') {
                            status.textContent = 'Completed! Download your results below.';
                            status.className = 'status completed';
                            submitBtn.disabled = false;
                            downloadSection.style.display = 'block';
                            
                            // Set download link - use the most recent file
                            const availableFiles = data.available_files || [];
                            if (availableFiles.length > 0) {
                                const latestFile = availableFiles[availableFiles.length - 1];
                                downloadLink.href = `/download/${latestFile}`;
                                downloadLink.textContent = `Download ${latestFile}`;
                            } else if (data.output_file) {
                                downloadLink.href = `/download/${data.output_file}`;
                                downloadLink.textContent = `Download ${data.output_file}`;
                            }
                            
                            clearInterval(pollInterval);
                        } else if (data.status === 'error') {
                            status.textContent = 'Error occurred during scraping';
                            status.className = 'status error';
                            submitBtn.disabled = false;
                            clearInterval(pollInterval);
                        }
                        
                    } catch (error) {
                        console.error('Status polling error:', error);
                        status.textContent = 'Connection error';
                        status.className = 'status error';
                        submitBtn.disabled = false;
                        clearInterval(pollInterval);
                    }
                }, 3000);
            }
        </script>
    </body>
    </html>
    '''

@app.route('/scrape', methods=['POST'])
def scrape():
    """Start scraping process"""
    try:
        data = request.json
        search_query = data.get('search_query')
        output_format = data.get('output_format', 'excel')
        healdessmode = data.get('healdessmode', 1)  # Default to headless mode
        
        if not search_query:
            return jsonify({"status": "error", "message": "Search query is required"}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())[:8]
        
        # Reset communicator
        railway_comm.messages = []
        railway_comm.status = "running"
        railway_comm.job_id = job_id
        railway_comm.search_query = search_query
        railway_comm.output_format = output_format
        railway_comm.scraped_data = []
        railway_comm.output_file = None
        
        # Start scraping in background thread
        def run_scraper():
            try:
                railway_comm.show_message(f"Starting scraping job {job_id}")
                railway_comm.show_message(f"Search query: {search_query}")
                railway_comm.show_message("Initializing Chrome in headless mode...")
                railway_comm.show_message("Note: Arabic and international searches are supported")
                
                # Set up communicator for Railway environment FIRST
                # Create a mock frontend object for the communicator
                class RailwayFrontend:
                    def __init__(self, comm):
                        self.comm = comm
                        self.outputFormatValue = output_format
                    
                    def messageshowing(self, message):
                        self.comm.show_message(message)
                    
                    def end_processing(self):
                        self.comm.end_processing()
                
                # Create mock frontend and set it in communicator
                railway_frontend = RailwayFrontend(railway_comm)
                Communicator.set_frontend_object(railway_frontend)
                
                # Create mock backend object for communicator
                class RailwayBackend:
                    def __init__(self, query):
                        self.searchquery = query
                
                railway_backend = RailwayBackend(search_query)
                Communicator.set_backend_object(railway_backend)
                
                # Now create backend with headless mode (note: original code has typo 'healdessmode')
                backend = Backend(search_query, output_format, healdessmode=healdessmode)
                
                # Run scraping
                railway_comm.show_message("Starting scraping process...")
                backend.mainscraping()
                
                # The scraping process will handle data saving automatically
                # through the existing DataSaver in the scraper
                railway_comm.show_message("Data saving completed automatically")
                
                railway_comm.status = "completed"
                railway_comm.show_message(f"Job {job_id} completed successfully!")
                railway_comm.show_message("Check the output folder for your scraped data")
                
            except Exception as e:
                railway_comm.status = "error"
                railway_comm.show_error_message(f"Job {job_id} failed: {str(e)}", "RAILWAY_ERROR")
                print(f"Scraping error: {str(e)}")
        
        thread = threading.Thread(target=run_scraper)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "started", 
            "message": f"Scraping started with job ID: {job_id}",
            "job_id": job_id
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status')
def status():
    """Get current scraping status"""
    # Check for output files in the output directory
    output_files = []
    if os.path.exists('output'):
        output_files = [f for f in os.listdir('output') if f.endswith(('.xlsx', '.csv', '.json'))]
    
    return jsonify({
        "status": railway_comm.status,
        "messages": railway_comm.messages[-50:],  # Last 50 messages to show more debug info
        "job_id": railway_comm.job_id,
        "output_file": railway_comm.output_file,
        "available_files": output_files
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download scraped data file"""
    try:
        file_path = os.path.join('output', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy", 
        "platform": "Railway",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/jobs')
def get_jobs():
    """Get list of recent jobs"""
    return jsonify({
        "current_job": {
            "id": railway_comm.job_id,
            "status": railway_comm.status,
            "query": getattr(railway_comm, 'search_query', None)
        }
    })

if __name__ == '__main__':
    # Railway will set PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Railway Flask app on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
