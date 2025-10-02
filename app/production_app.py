"""
Production Flask Web Application for Google Maps Scraper
Optimized for DigitalOcean deployment with headless Chrome
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

class ProductionCommunicator:
    """Custom communicator for Production web interface"""
    def __init__(self):
        self.messages = []
        self.status = "ready"
        self.job_id = None
        self.scraped_data = []
        self.output_file = None
    
    def show_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {message}")
        print(f"Production: {message}")
    
    def show_error_message(self, message, error_code):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] ERROR: {message} (Code: {error_code})")
        print(f"Production ERROR: {message}")
    
    def end_processing(self):
        self.status = "completed"
    
    def get_output_format(self):
        return getattr(self, 'output_format', 'excel')
    
    def get_search_query(self):
        return getattr(self, 'search_query', 'unknown')

# Global communicator instance
# Session-based communicators for production (thread-safe)
import threading
session_communicators = {}
session_lock = threading.Lock()

# Helper functions for session management
def get_session_communicator(session_id):
    """Get or create a communicator for a specific session"""
    with session_lock:
        if session_id not in session_communicators:
            session_communicators[session_id] = ProductionCommunicator()
        return session_communicators[session_id]

def cleanup_session(session_id):
    """Clean up resources for a completed session"""
    with session_lock:
        if session_id in session_communicators:
            del session_communicators[session_id]

@app.route('/')
def index():
    """Main web interface"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ORIZON Google Maps Scraper</title>
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAwIiBoZWlnaHQ9IjUwMCIgdmlld0JveD0iMCAwIDUwMCA1MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MDAiIGhlaWdodD0iNTAwIiByeD0iMTAwIiBmaWxsPSIjMjcyODYwIi8+CjxjaXJjbGUgY3g9IjI1MCIgY3k9IjI1MCIgcj0iMTUwIiBmaWxsPSIjZjhjODAwIi8+CjxjaXJjbGUgY3g9IjI1MCIgY3k9IjI1MCIgcj0iNzUiIGZpbGw9IiMyNzI4NjAiLz4KPGNpcmNsZSBjeD0iNDIwIiBjeT0iMTMwIiByPSIxNSIgZmlsbD0iI2Y4Yzg0NSIgc3Ryb2tlPSIjZjhjODAwIiBzdHJva2Utd2lkdGg9IjMiLz4KPC9zdmc+">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #272860 0%, #1a1b4b 100%);
                color: white;
                min-height: 100vh;
                overflow-x: hidden;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
            }

            .logo {
                max-width: 200px;
                height: auto;
                margin-bottom: 20px;
            }

            .title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #f8c800;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .subtitle {
                font-size: 1.2rem;
                color: #e0e0e0;
                font-weight: 300;
            }

            .main-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 40px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                margin-bottom: 30px;
            }

            .form-group {
                margin-bottom: 25px;
            }

            .form-label {
                display: block;
                font-size: 1.1rem;
                font-weight: 600;
                color: #f8c800;
                margin-bottom: 8px;
            }

            .form-input {
                width: 100%;
                padding: 15px;
                font-size: 1rem;
                border: 2px solid rgba(248, 200, 0, 0.3);
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                transition: all 0.3s ease;
            }

            .form-input:focus {
                outline: none;
                border-color: #f8c800;
                background: rgba(255, 255, 255, 0.15);
                box-shadow: 0 0 20px rgba(248, 200, 0, 0.3);
            }

            .form-input::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }

            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 20px;
            }

            .checkbox {
                width: 20px;
                height: 20px;
                accent-color: #f8c800;
            }

            .start-button {
                width: 100%;
                padding: 18px;
                font-size: 1.2rem;
                font-weight: 700;
                background: linear-gradient(45deg, #f8c800, #ffd700);
                color: #272860;
                border: none;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .start-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(248, 200, 0, 0.4);
            }

            .start-button:active {
                transform: translateY(0);
            }

            .start-button:disabled {
                background: #666;
                color: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }

            /* Tab Styles */
            .tabs {
                display: flex;
                justify-content: center;
                margin-bottom: 30px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 5px;
                backdrop-filter: blur(10px);
            }

            .tab {
                flex: 1;
                padding: 15px 20px;
                text-align: center;
                cursor: pointer;
                border-radius: 10px;
                transition: all 0.3s ease;
                color: #ccc;
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .tab:hover {
                background: rgba(248, 200, 0, 0.1);
                color: #f8c800;
            }

            .tab.active {
                background: linear-gradient(45deg, #f8c800, #ffd700);
                color: #272860;
                box-shadow: 0 4px 15px rgba(248, 200, 0, 0.3);
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
            }

            /* History Styles */
            .history-list {
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid rgba(248, 200, 0, 0.2);
                border-radius: 10px;
                padding: 15px;
            }

            .history-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                margin-bottom: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border-left: 4px solid #f8c800;
                transition: all 0.3s ease;
            }

            .history-item:hover {
                background: rgba(248, 200, 0, 0.1);
                transform: translateX(5px);
            }

            .history-item:last-child {
                margin-bottom: 0;
            }

            .history-info {
                flex: 1;
            }

            .history-filename {
                color: #f8c800;
                font-weight: 600;
                margin-bottom: 5px;
                word-break: break-word;
            }

            .history-details {
                color: #ccc;
                font-size: 0.9rem;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }

            .history-download {
                padding: 8px 16px;
                background: linear-gradient(45deg, #f8c800, #ffd700);
                color: #272860;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                white-space: nowrap;
            }

            .history-download:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(248, 200, 0, 0.4);
            }

            .progress-section {
                display: none;
                margin-top: 30px;
            }

            .progress-bar {
                width: 100%;
                height: 15px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #f8c800, #ffd700);
                width: 0%;
                transition: width 0.3s ease;
                border-radius: 10px;
            }

            .status-text {
                text-align: center;
                font-size: 1.1rem;
                color: #f8c800;
                font-weight: 600;
            }

            .results-section {
                display: none;
                margin-top: 30px;
            }

            .download-button {
                display: inline-block;
                padding: 12px 25px;
                background: linear-gradient(45deg, #f8c800, #ffd700);
                color: #272860;
                text-decoration: none;
                border-radius: 10px;
                font-weight: 600;
                margin-right: 15px;
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }

            .download-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(248, 200, 0, 0.3);
            }

            .footer {
                text-align: center;
                padding: 20px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 0.9rem;
            }

            .orizon-accent {
                color: #f8c800;
            }

            /* Live extraction styles */
            .live-extraction-box {
                max-height: 350px; 
                overflow-y: auto; 
                background: rgba(0,0,0,0.3); 
                border-radius: 10px; 
                padding: 15px; 
                border: 1px solid rgba(248, 200, 0, 0.3);
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

            /* Scrollbar styling */
            .live-extraction-box::-webkit-scrollbar {
                width: 8px;
            }

            .live-extraction-box::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }

            .live-extraction-box::-webkit-scrollbar-thumb {
                background: #f8c800;
                border-radius: 4px;
            }

            .live-extraction-box::-webkit-scrollbar-thumb:hover {
                background: #ffd700;
            }

            @media (max-width: 768px) {
                .title {
                    font-size: 2rem;
                }
                
                .main-card {
                    padding: 25px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <!-- ORIZON Logo SVG -->
                <svg class="logo" width="150" height="60" viewBox="0 0 300 120" xmlns="http://www.w3.org/2000/svg">
                    <!-- Main O Shape -->
                    <circle cx="60" cy="60" r="45" fill="#f8c800" stroke="none"/>
                    <circle cx="60" cy="60" r="22" fill="#272860"/>
                    
                    <!-- Copyright symbol -->
                    <circle cx="220" cy="35" r="8" fill="none" stroke="#f8c800" stroke-width="2"/>
                    <text x="220" y="40" text-anchor="middle" fill="#f8c800" font-family="Arial, sans-serif" font-size="10" font-weight="bold">©</text>
                    
                    <!-- Text "RIZON" -->
                    <text x="140" y="75" fill="#f8c800" font-family="Arial, sans-serif" font-size="36" font-weight="bold">RIZON</text>
                </svg>
                <h1 class="title">Multi-Purpose Scraper</h1>
                <p class="subtitle">Extract business data and emails with ease</p>
            </div>

            <!-- Tab Navigation -->
            <div class="tabs">
                <div class="tab active" data-tab="maps">
                    <i class="fas fa-map-marker-alt"></i>
                    Google Maps
                </div>
                <div class="tab" data-tab="history">
                    <i class="fas fa-history"></i>
                    History
                </div>
            </div>

            <!-- Maps Tab Content -->
            <div class="tab-content active" id="maps-tab">
                <div class="main-card">
                    <form id="scraperForm">
                    <div class="form-group">
                        <label class="form-label" for="search_query">Search Query</label>
                        <input type="text" id="search_query" name="search_query" class="form-input" 
                               placeholder="e.g., restaurants in Cairo, Egypt" required>
                    </div>

                    <div class="checkbox-group">
                        <input type="checkbox" id="headless" name="headless" class="checkbox" checked>
                        <label for="headless" class="form-label">Run in headless mode (recommended)</label>
                    </div>

                    <button type="submit" class="start-button" id="startButton">
                        START SCRAPING
                    </button>
                </form>

                <div class="progress-section" id="progressSection">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="status-text" id="statusText">Initializing...</div>
                    
                    <!-- Live extraction display -->
                    <div id="liveExtractionContainer" style="margin-top: 20px; display: none;">
                        <h4 style="color: #f8c800; margin-bottom: 5px;">📊 Live Extraction Progress</h4>
                        <p style="color: #ccc; margin-bottom: 15px; font-size: 0.85rem;">Real-time scraping progress and debug information</p>
                        <div id="liveExtractionBox" class="live-extraction-box">
                            <!-- Live extraction data will appear here -->
                        </div>
                    </div>
                </div>

                <div class="results-section" id="resultsSection">
                    <h3 style="color: #f8c800; margin-bottom: 15px;">Scraping Complete!</h3>
                    <p style="margin-bottom: 20px;" id="resultsText">Your data has been successfully extracted and saved.</p>
                    
                    <!-- Download buttons -->
                    <div style="margin-bottom: 30px;">
                        <a href="#" class="download-button" id="downloadExcel">📊 Download Excel</a>
                        <a href="#" class="download-button" id="downloadCsv">📄 Download CSV</a>
                        <a href="#" class="download-button" id="downloadJson">📋 Download JSON</a>
                    </div>
                </div>
            </div>
            </div> <!-- End Maps Tab -->

            <!-- History Tab Content -->
            <div class="tab-content" id="history-tab">
                <div class="main-card">
                    <h2 style="color: #f8c800; margin-bottom: 20px;">📁 Scraping History</h2>
                    <p style="color: #ccc; margin-bottom: 20px;">All your scraped files are listed below. Click to download.</p>
                    
                    <div id="historyLoading" style="text-align: center; color: #ccc; padding: 20px;">
                        <i class="fas fa-spinner fa-spin"></i> Loading history...
                    </div>
                    
                    <div id="historyContent" style="display: none;">
                        <div id="historyList" class="history-list">
                            <!-- History items will be populated here -->
                        </div>
                        
                        <button id="refreshHistory" class="start-button" style="margin-top: 20px;">
                            <i class="fas fa-sync-alt"></i> Refresh History
                        </button>
                    </div>
                    
                    <div id="noHistory" style="display: none; text-align: center; color: #ccc; padding: 40px;">
                        <i class="fas fa-folder-open" style="font-size: 48px; margin-bottom: 20px; opacity: 0.5;"></i>
                        <p>No scraping history found.</p>
                        <p style="font-size: 0.9rem; margin-top: 10px;">Start scraping to see your files here!</p>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>&copy; 2025 <span class="orizon-accent">ORIZON</span>. All rights reserved.</p>
            </div>
        </div>

        <script>
            class GoogleMapsScraper {
                constructor() {
                    this.form = document.getElementById('scraperForm');
                    this.startButton = document.getElementById('startButton');
                    this.progressSection = document.getElementById('progressSection');
                    this.resultsSection = document.getElementById('resultsSection');
                    this.progressFill = document.getElementById('progressFill');
                    this.statusText = document.getElementById('statusText');
                    this.downloadExcel = document.getElementById('downloadExcel');
                    this.downloadCsv = document.getElementById('downloadCsv');
                    this.downloadJson = document.getElementById('downloadJson');
                    this.extractedData = null;
                    
                    this.init();
                }

                init() {
                    this.form.addEventListener('submit', this.handleSubmit.bind(this));
                }

                async handleSubmit(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this.form);
                    const data = {
                        search_query: formData.get('search_query'),
                        output_format: 'excel',
                        healdessmode: formData.has('headless') ? 1 : 0
                    };

                    this.startScraping(data);
                }

                async startScraping(data) {
                    // Disable form and show progress
                    this.startButton.disabled = true;
                    this.startButton.textContent = 'Scraping...';
                    this.progressSection.style.display = 'block';
                    this.resultsSection.style.display = 'none';

                    try {
                        // Start the scraping process
                        const response = await fetch('/scrape', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });

                        if (!response.ok) {
                            throw new Error('Failed to start scraping');
                        }

                        const result = await response.json();
                        console.log(result);

                        if (result.status === 'started') {
                            this.statusText.textContent = 'Scraping in progress...';
                            this.currentJobId = result.job_id; // Store job ID for session tracking
                            console.log('Started scraping job:', this.currentJobId);
                            this.pollStatus();
                        } else {
                            this.statusText.textContent = 'Error starting scraping';
                            this.startButton.disabled = false;
                            this.startButton.textContent = 'START SCRAPING';
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        this.statusText.textContent = 'Error starting scraping';
                        this.startButton.disabled = false;
                        this.startButton.textContent = 'START SCRAPING';
                    }
                }

                async pollStatus() {
                    const pollInterval = setInterval(async () => {
                        try {
                            // Use session-specific status endpoint if we have a job ID
                            const statusUrl = this.currentJobId ? `/status/${this.currentJobId}` : '/status';
                            console.log('Polling status for:', statusUrl);
                            const response = await fetch(statusUrl);
                            const data = await response.json();
                            
                            this.statusText.textContent = data.status;
                            
                            // Update progress bar based on status
                            if (data.status === 'running') {
                                this.progressFill.style.width = '70%';
                            } else if (data.status === 'completed') {
                                this.progressFill.style.width = '100%';
                            }
                            
                            // Update live extraction messages
                            if (data.messages && data.messages.length > 0) {
                                this.showLiveExtraction(data.messages);
                            }
                            
                            if (data.status === 'completed') {
                                this.showResults(data);
                                clearInterval(pollInterval);
                            } else if (data.status === 'error') {
                                this.statusText.textContent = 'Error occurred during scraping';
                                this.startButton.disabled = false;
                                this.startButton.textContent = 'START SCRAPING';
                                clearInterval(pollInterval);
                            }
                            
                        } catch (error) {
                            console.error('Status polling error:', error);
                        }
                    }, 3000);
                }

                showLiveExtraction(messages) {
                    const container = document.getElementById('liveExtractionContainer');
                    const box = document.getElementById('liveExtractionBox');
                    
                    // Show the container
                    container.style.display = 'block';
                    
                    // Update the live extraction box
                    box.innerHTML = messages.map(msg => {
                        let className = 'message';
                        if (msg.includes('ERROR')) className += ' error';
                        else if (msg.includes('completed') || msg.includes('success')) className += ' success';
                        else className += ' info';
                        
                        return `<div class="${className}">${msg}</div>`;
                    }).join('');
                    
                    box.scrollTop = box.scrollHeight;
                }

                async showResults(data) {
                    this.progressSection.style.display = 'none';
                    this.resultsSection.style.display = 'block';
                    
                    // Reset button state
                    this.startButton.disabled = false;
                    this.startButton.textContent = 'START SCRAPING';
                    
                    // Update results text
                    const resultsText = document.querySelector('#resultsText');
                    resultsText.textContent = 'Your scraping is complete! Download your results below.';
                    
                    // ALWAYS fetch the latest files from /files endpoint to ensure we get the most recent file
                    console.log('Scraping completed, fetching latest files...');
                    await this.fetchLatestFiles();
                    
                    // Also refresh history if history tab exists
                    if (window.tabManager) {
                        window.tabManager.loadHistory(true);
                    }
                }

                async fetchLatestFiles() {
                    try {
                        console.log('Fetching latest files from /files endpoint...');
                        const response = await fetch('/files');
                        const data = await response.json();
                        console.log('Latest files response:', data);
                        
                        const files = data.files || [];
                        const filesWithDetails = data.files_with_details || [];
                        
                        if (files.length > 0) {
                            // Files are already sorted by modification time (most recent first) from the server
                            console.log('Latest files (sorted by server):', files);
                            console.log('Files with details:', filesWithDetails);
                            
                            // Show the most recent file of each type
                            const recentXlsx = files.find(f => f.endsWith('.xlsx'));
                            const recentCsv = files.find(f => f.endsWith('.csv'));
                            const recentJson = files.find(f => f.endsWith('.json'));
                            
                            console.log('Most recent files:', { recentXlsx, recentCsv, recentJson });
                            
                            // Show file details if available
                            if (recentXlsx && filesWithDetails.length > 0) {
                                const xlsxDetails = filesWithDetails.find(f => f.filename === recentXlsx);
                                if (xlsxDetails) {
                                    const modTime = new Date(xlsxDetails.mod_time * 1000);
                                    console.log(`Latest Excel file: ${recentXlsx} (created: ${modTime.toLocaleString()})`);
                                }
                            }
                            
                            if (recentXlsx) {
                                this.downloadExcel.href = `/download/${encodeURIComponent(recentXlsx)}`;
                                this.downloadExcel.textContent = `📊 Download ${recentXlsx}`;
                                this.downloadExcel.style.display = 'inline-block';
                                console.log('✅ Set Excel download link to LATEST file:', recentXlsx);
                            }
                            if (recentCsv) {
                                this.downloadCsv.href = `/download/${encodeURIComponent(recentCsv)}`;
                                this.downloadCsv.textContent = `📄 Download ${recentCsv}`;
                                this.downloadCsv.style.display = 'inline-block';
                                console.log('✅ Set CSV download link to LATEST file:', recentCsv);
                            }
                            if (recentJson) {
                                this.downloadJson.href = `/download/${encodeURIComponent(recentJson)}`;
                                this.downloadJson.textContent = `📋 Download ${recentJson}`;
                                this.downloadJson.style.display = 'inline-block';
                                console.log('✅ Set JSON download link to LATEST file:', recentJson);
                            }
                        } else {
                            console.log('❌ No files found in /files endpoint');
                            this.downloadExcel.textContent = 'No files available';
                            this.downloadExcel.style.display = 'none';
                            this.downloadCsv.style.display = 'none';
                            this.downloadJson.style.display = 'none';
                        }
                    } catch (error) {
                        console.error('❌ Error fetching latest files:', error);
                        // Fallback to old method
                        this.fetchAvailableFiles();
                    }
                }

                async fetchAvailableFiles() {
                    try {
                        console.log('Fetching available files from /files endpoint...');
                        const response = await fetch('/files');
                        const data = await response.json();
                        console.log('Files response:', data);
                        
                        const files = data.files || [];
                        if (files.length > 0) {
                            // Files are already sorted by modification time (most recent first) from the server
                            console.log('Files already sorted by server:', files);
                            console.log('Files with details:', data.files_with_details);
                            
                            // Show the most recent file of each type
                            const recentXlsx = files.find(f => f.endsWith('.xlsx'));
                            const recentCsv = files.find(f => f.endsWith('.csv'));
                            const recentJson = files.find(f => f.endsWith('.json'));
                            
                            console.log('Most recent files:', { recentXlsx, recentCsv, recentJson });
                            
                            if (recentXlsx) {
                                this.downloadExcel.href = `/download/${encodeURIComponent(recentXlsx)}`;
                                this.downloadExcel.textContent = `📊 Download ${recentXlsx}`;
                                this.downloadExcel.style.display = 'inline-block';
                                console.log('Set Excel download link to:', recentXlsx);
                            }
                            if (recentCsv) {
                                this.downloadCsv.href = `/download/${encodeURIComponent(recentCsv)}`;
                                this.downloadCsv.textContent = `📄 Download ${recentCsv}`;
                                this.downloadCsv.style.display = 'inline-block';
                                console.log('Set CSV download link to:', recentCsv);
                            }
                            if (recentJson) {
                                this.downloadJson.href = `/download/${encodeURIComponent(recentJson)}`;
                                this.downloadJson.textContent = `📋 Download ${recentJson}`;
                                this.downloadJson.style.display = 'inline-block';
                                console.log('Set JSON download link to:', recentJson);
                            }
                        } else {
                            console.log('No files found in /files endpoint');
                            this.downloadExcel.textContent = 'No files available';
                            this.downloadExcel.style.display = 'none';
                            this.downloadCsv.style.display = 'none';
                            this.downloadJson.style.display = 'none';
                        }
                    } catch (error) {
                        console.error('Error fetching files:', error);
                    }
                }
            }

            // Tab Management
            class TabManager {
                constructor() {
                    this.init();
                }

                init() {
                    // Add click listeners to tabs
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.addEventListener('click', (e) => {
                            const tabName = e.currentTarget.getAttribute('data-tab');
                            this.switchTab(tabName);
                        });
                    });

                    // Load history when history tab is first clicked
                    document.querySelector('[data-tab="history"]').addEventListener('click', () => {
                        this.loadHistory();
                    });

                    // Refresh history button
                    document.getElementById('refreshHistory').addEventListener('click', () => {
                        this.loadHistory(true);
                    });
                }

                switchTab(tabName) {
                    // Remove active class from all tabs and content
                    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

                    // Add active class to selected tab and content
                    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
                    document.getElementById(`${tabName}-tab`).classList.add('active');
                }

                async loadHistory(forceRefresh = false) {
                    const historyLoading = document.getElementById('historyLoading');
                    const historyContent = document.getElementById('historyContent');
                    const noHistory = document.getElementById('noHistory');
                    const historyList = document.getElementById('historyList');

                    // Show loading state
                    historyLoading.style.display = 'block';
                    historyContent.style.display = 'none';
                    noHistory.style.display = 'none';

                    try {
                        console.log('Loading history...');
                        const response = await fetch('/files');
                        const data = await response.json();
                        console.log('History data:', data);

                        const files = data.files || [];
                        const filesWithDetails = data.files_with_details || [];

                        if (files.length === 0) {
                            historyLoading.style.display = 'none';
                            noHistory.style.display = 'block';
                            return;
                        }

                        // Create history items
                        historyList.innerHTML = '';
                        
                        files.forEach((filename, index) => {
                            const fileDetails = filesWithDetails.find(f => f.filename === filename);
                            const modTime = fileDetails ? new Date(fileDetails.mod_time * 1000) : new Date();
                            const fileSize = this.getFileSize(filename);
                            
                            const historyItem = document.createElement('div');
                            historyItem.className = 'history-item';
                            
                            // Extract search query from filename
                            const searchQuery = filename.replace(' - GMS output', '').replace(/\s*\(\d+\)\.xlsx$/, '').replace(/\.xlsx$/, '');
                            
                            historyItem.innerHTML = `
                                <div class="history-info">
                                    <div class="history-filename">${filename}</div>
                                    <div class="history-details">
                                        <span><i class="fas fa-search"></i> ${searchQuery}</span>
                                        <span><i class="fas fa-clock"></i> ${modTime.toLocaleString()}</span>
                                        <span><i class="fas fa-file-excel"></i> Excel</span>
                                    </div>
                                </div>
                                <a href="/download/${encodeURIComponent(filename)}" class="history-download">
                                    <i class="fas fa-download"></i> Download
                                </a>
                            `;
                            
                            historyList.appendChild(historyItem);
                        });

                        historyLoading.style.display = 'none';
                        historyContent.style.display = 'block';

                    } catch (error) {
                        console.error('Error loading history:', error);
                        historyLoading.style.display = 'none';
                        noHistory.style.display = 'block';
                    }
                }

                getFileSize(filename) {
                    // This would require a separate API call to get file sizes
                    // For now, return a placeholder
                    return 'Unknown size';
                }
            }

            // Initialize everything when page loads
            document.addEventListener('DOMContentLoaded', () => {
                window.scraperInstance = new GoogleMapsScraper();
                window.tabManager = new TabManager();
            });
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
        
        # Generate unique job ID (this will be our session ID)
        job_id = str(uuid.uuid4())[:8]
        
        # Get session-specific communicator
        session_comm = get_session_communicator(job_id)
        
        # Reset session communicator
        session_comm.messages = []
        session_comm.status = "running"
        session_comm.job_id = job_id
        session_comm.search_query = search_query
        session_comm.output_format = output_format
        session_comm.scraped_data = []
        session_comm.output_file = None
        
        # Start scraping in background thread
        def run_scraper():
            try:
                session_comm.show_message(f"Starting scraping job {job_id}")
                session_comm.show_message(f"Search query: {search_query}")
                session_comm.show_message("Initializing Chrome in headless mode...")
                session_comm.show_message("Note: Arabic and international searches are supported")
                
                # Set up communicator for Production environment FIRST
                # Create a mock frontend object for the communicator
                class SessionFrontend:
                    def __init__(self, comm):
                        self.comm = comm
                        self.outputFormatValue = output_format
                        self.session_id = job_id  # Track session ID
                    
                    def messageshowing(self, message):
                        self.comm.show_message(message)
                    
                    def end_processing(self):
                        self.comm.end_processing()
                
                # Create session-specific frontend and set it in communicator
                session_frontend = SessionFrontend(session_comm)
                Communicator.set_frontend_object(session_frontend)
                
                # Create mock backend object for communicator
                class ProductionBackend:
                    def __init__(self, query):
                        self.searchquery = query
                
                production_backend = ProductionBackend(search_query)
                Communicator.set_backend_object(production_backend)
                
                # Now create backend with headless mode (note: original code has typo 'healdessmode')
                backend = Backend(search_query, output_format, healdessmode=healdessmode)
                
                # Run scraping
                session_comm.show_message("Starting scraping process...")
                backend.mainscraping()
                
                # The scraping process will handle data saving automatically
                # through the existing DataSaver in the scraper
                session_comm.show_message("Data saving completed automatically")
                
                # Check what files were actually created in multiple possible locations
                possible_output_dirs = ['output', '../output', '/root/scrapper-v2/output', '/root/scrapper-v2/app/output']
                created_files = []
                
                for output_dir in possible_output_dirs:
                    if os.path.exists(output_dir):
                        try:
                            files = [f for f in os.listdir(output_dir) if f.endswith(('.xlsx', '.csv', '.json'))]
                            created_files.extend(files)
                            session_comm.show_message(f"Found {len(files)} files in {output_dir}")
                        except Exception as e:
                            session_comm.show_message(f"Error reading {output_dir}: {e}")
                
                if created_files:
                    # Remove duplicates
                    created_files = list(dict.fromkeys(created_files))
                    # Get the most recent file by finding it in any directory
                    latest_file = None
                    latest_time = 0
                    for file in created_files:
                        for output_dir in possible_output_dirs:
                            file_path = os.path.join(output_dir, file)
                            if os.path.exists(file_path):
                                file_time = os.path.getctime(file_path)
                                if file_time > latest_time:
                                    latest_time = file_time
                                    latest_file = file
                    
                    if latest_file:
                        session_comm.output_file = latest_file
                        session_comm.show_message(f"Output file created: {latest_file}")
                        session_comm.show_message(f"All available files: {', '.join(created_files)}")
                else:
                    session_comm.show_message("No output files found in any output directory")
                    session_comm.show_message(f"Checked directories: {', '.join(possible_output_dirs)}")
                
                session_comm.status = "completed"
                session_comm.show_message(f"Job {job_id} completed successfully!")
                session_comm.show_message("Check the output folder for your scraped data")
                
                # Clean up session after a delay (keep it for status checking)
                def delayed_cleanup():
                    import time
                    time.sleep(300)  # Keep session for 5 minutes for status checking
                    cleanup_session(job_id)
                
                threading.Thread(target=delayed_cleanup, daemon=True).start()
                
            except Exception as e:
                session_comm.status = "error"
                session_comm.show_error_message(f"Job {job_id} failed: {str(e)}", "PRODUCTION_ERROR")
                print(f"Scraping error for session {job_id}: {str(e)}")
                
                # Clean up failed session after a delay
                def delayed_cleanup():
                    import time
                    time.sleep(60)  # Keep failed session for 1 minute
                    cleanup_session(job_id)
                
                threading.Thread(target=delayed_cleanup, daemon=True).start()
        
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
@app.route('/status/<job_id>')
def status(job_id=None):
    """Get current scraping status for a specific session"""
    # Check for output files in multiple possible output directories (prioritize main output dir)
    all_files_with_time = []
    possible_output_dirs = ['/root/scrapper-v2/output', 'output', '../output', '/root/scrapper-v2/app/output']
    
    for output_dir in possible_output_dirs:
        if os.path.exists(output_dir):
            try:
                all_files = os.listdir(output_dir)
                files = [f for f in all_files if f.endswith(('.xlsx', '.csv', '.json'))]
                
                # Get file modification times for sorting
                for f in files:
                    file_path = os.path.join(output_dir, f)
                    if os.path.isfile(file_path):
                        mod_time = os.path.getmtime(file_path)
                        all_files_with_time.append((f, mod_time, output_dir))
                
                print(f"DEBUG: Found {len(files)} files in {output_dir}: {files}")
            except Exception as e:
                print(f"DEBUG: Error reading {output_dir}: {e}")
    
    # Remove duplicates by filename (keep the one with latest modification time)
    unique_files = {}
    for filename, mod_time, output_dir in all_files_with_time:
        if filename not in unique_files or mod_time > unique_files[filename][1]:
            unique_files[filename] = (filename, mod_time, output_dir)
    
    # Sort by modification time (most recent first)
    sorted_files = sorted(unique_files.values(), key=lambda x: x[1], reverse=True)
    output_files = [f[0] for f in sorted_files]  # Extract just the filenames
    
    print(f"DEBUG: Status endpoint - Final sorted files (most recent first): {output_files}")
    
    # If job_id is provided, get session-specific status
    if job_id:
        with session_lock:
            if job_id in session_communicators:
                session_comm = session_communicators[job_id]
                return jsonify({
                    "status": session_comm.status,
                    "messages": session_comm.messages[-50:],  # Last 50 messages to show more debug info
                    "job_id": session_comm.job_id,
                    "search_query": session_comm.get_search_query(),
                    "output_file": session_comm.output_file,
                    "available_files": output_files,
                    "checked_directories": [d for d in possible_output_dirs if os.path.exists(d)]
                })
            else:
                return jsonify({
                    "status": "not_found",
                    "message": f"Session {job_id} not found or expired",
                    "available_files": output_files,
                    "checked_directories": [d for d in possible_output_dirs if os.path.exists(d)]
                })
    
    # If no job_id provided, return general status (for backward compatibility)
    # Try to find the most recent active session
    with session_lock:
        if session_communicators:
            # Get the most recent session
            latest_session = max(session_communicators.values(), key=lambda x: getattr(x, 'job_id', ''))
            return jsonify({
                "status": latest_session.status,
                "messages": latest_session.messages[-50:],
                "job_id": latest_session.job_id,
                "search_query": latest_session.get_search_query(),
                "output_file": latest_session.output_file,
                "available_files": output_files,
                "checked_directories": [d for d in possible_output_dirs if os.path.exists(d)]
            })
        else:
            return jsonify({
                "status": "idle",
                "messages": [],
                "job_id": None,
                "search_query": None,
                "output_file": None,
                "available_files": output_files,
                "checked_directories": [d for d in possible_output_dirs if os.path.exists(d)]
            })

@app.route('/files')
def list_files():
    """List all available files for download"""
    all_files_with_time = []
    # Check multiple possible output directories (prioritize main output dir)
    possible_output_dirs = ['/root/scrapper-v2/output', 'output', '../output', '/root/scrapper-v2/app/output']
    
    for output_dir in possible_output_dirs:
        if os.path.exists(output_dir):
            try:
                all_files = os.listdir(output_dir)
                files = [f for f in all_files if f.endswith(('.xlsx', '.csv', '.json'))]
                
                # Get file modification times for sorting
                for f in files:
                    file_path = os.path.join(output_dir, f)
                    if os.path.isfile(file_path):
                        mod_time = os.path.getmtime(file_path)
                        all_files_with_time.append((f, mod_time, output_dir))
                
                print(f"DEBUG: Found {len(files)} files in {output_dir}: {files}")
            except Exception as e:
                print(f"DEBUG: Error reading {output_dir}: {e}")
    
    # Remove duplicates by filename (keep the one with latest modification time)
    unique_files = {}
    for filename, mod_time, output_dir in all_files_with_time:
        if filename not in unique_files or mod_time > unique_files[filename][1]:
            unique_files[filename] = (filename, mod_time, output_dir)
    
    # Sort by modification time (most recent first)
    sorted_files = sorted(unique_files.values(), key=lambda x: x[1], reverse=True)
    output_files = [f[0] for f in sorted_files]  # Extract just the filenames
    
    print(f"DEBUG: Final sorted files (most recent first): {output_files}")
    
    if not output_files:
        print("DEBUG: No output files found in any directory")
    
    return jsonify({
        "files": output_files,
        "files_with_details": [{"filename": f[0], "mod_time": f[1], "directory": f[2]} for f in sorted_files]
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download scraped data file"""
    try:
        import urllib.parse
        
        # URL decode the filename to handle Arabic characters
        decoded_filename = urllib.parse.unquote(filename)
        print(f"DEBUG: Download requested for: {filename}")
        print(f"DEBUG: Decoded filename: {decoded_filename}")
        
        # Try multiple possible output directories (prioritize the ones that actually exist)
        possible_paths = [
            # First try the main output directory where files actually exist
            os.path.join('/root/scrapper-v2/output', decoded_filename),  # Main output directory
            os.path.join('/root/scrapper-v2/output', filename),  # Main output directory encoded
            # Then try other possible locations
            os.path.join('output', decoded_filename),  # Current directory
            os.path.join('output', filename),  # Original encoded filename
            os.path.join('..', 'output', decoded_filename),  # Parent directory
            os.path.join('..', 'output', filename),  # Parent directory with encoded
            os.path.join('/root/scrapper-v2/app/output', decoded_filename),  # App subdirectory
            os.path.join('/root/scrapper-v2/app/output', filename),  # App subdirectory encoded
        ]
        
        file_path = None
        for path in possible_paths:
            print(f"DEBUG: Checking path: {path}")
            if os.path.exists(path):
                file_path = path
                print(f"DEBUG: Found file at: {file_path}")
                break
        
        if file_path and os.path.exists(file_path):
            print(f"DEBUG: Sending file: {file_path}")
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            print(f"DEBUG: File not found in any expected location")
            
            # If specific file not found, try to find any recent file in any output directory
            for output_dir in ['/root/scrapper-v2/output', 'output', '../output', '/root/scrapper-v2/app/output']:
                if os.path.exists(output_dir):
                    try:
                        all_files = os.listdir(output_dir)
                        if all_files:
                            # Get the most recently modified file
                            files_with_time = [(f, os.path.getmtime(os.path.join(output_dir, f))) for f in all_files if os.path.isfile(os.path.join(output_dir, f))]
                            if files_with_time:
                                most_recent = max(files_with_time, key=lambda x: x[1])
                                most_recent_path = os.path.join(output_dir, most_recent[0])
                                print(f"DEBUG: Serving most recent file instead: {most_recent_path}")
                                return send_file(most_recent_path, as_attachment=True, download_name=most_recent[0])
                    except Exception as e:
                        print(f"DEBUG: Error checking {output_dir}: {e}")
                        continue
            
            # Check what directories and files actually exist
            debug_info = {
                "requested_filename": filename,
                "decoded_filename": decoded_filename,
                "current_working_dir": os.getcwd(),
                "checked_paths": possible_paths,
            }
            
            # Check if output directories exist
            output_dirs = ['output', '../output', '/root/scrapper-v2/output', '/root/scrapper-v2/app/output']
            existing_dirs = []
            for dir_path in output_dirs:
                if os.path.exists(dir_path):
                    existing_dirs.append(dir_path)
                    try:
                        files = os.listdir(dir_path)
                        debug_info[f"files_in_{dir_path}"] = files
                    except Exception as e:
                        debug_info[f"error_reading_{dir_path}"] = str(e)
            
            debug_info["existing_output_dirs"] = existing_dirs
            print(f"DEBUG: Debug info: {debug_info}")
            
            return jsonify({
                "error": "File not found", 
                "debug_info": debug_info
            }), 404
    except Exception as e:
        print(f"DEBUG: Download error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/debug/files')
def debug_files():
    """Debug endpoint to check files and permissions"""
    debug_info = {
        "output_dir_exists": os.path.exists('output'),
        "current_working_dir": os.getcwd(),
        "output_dir_path": os.path.abspath('output'),
        "timestamp": datetime.now().isoformat()
    }
    
    if os.path.exists('output'):
        try:
            all_files = os.listdir('output')
            debug_info["all_files"] = all_files
            debug_info["file_count"] = len(all_files)
            
            # Check file details
            file_details = []
            for file in all_files:
                file_path = os.path.join('output', file)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    file_details.append({
                        "name": file,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "readable": os.access(file_path, os.R_OK),
                        "path": file_path
                    })
            debug_info["file_details"] = file_details
            
        except Exception as e:
            debug_info["error"] = str(e)
    else:
        debug_info["error"] = "Output directory does not exist"
    
    return jsonify(debug_info)

@app.route('/health')
def health():
    """Health check endpoint for DigitalOcean"""
    return jsonify({
        "status": "healthy", 
        "platform": "DigitalOcean",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # DigitalOcean will set PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting DigitalOcean Flask app on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)