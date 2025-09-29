"""
Railway-specific settings for Google Maps Scraper
Optimized for Railway deployment environment
"""

# Railway Environment Configuration
OUTPUT_PATH = "/app/output"
DRIVER_EXECUTABLE_PATH = None

# Railway-specific Chrome options
RAILWAY_CHROME_OPTIONS = [
    '--headless',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--window-size=1920,1080',
    '--memory-pressure-off',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor'
]

# Railway environment detection
import os
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', False)
HEADLESS_MODE = 1 if RAILWAY_ENVIRONMENT else 0

# Memory optimization for Railway
MAX_MEMORY_USAGE = 80  # Percentage
MEMORY_CHECK_INTERVAL = 30  # Seconds

# Railway-specific timeouts
RAILWAY_TIMEOUT = 300  # 5 minutes
RAILWAY_RETRY_COUNT = 3

# Output file naming for Railway
OUTPUT_FILE_PREFIX = "railway_scrape"
OUTPUT_FILE_TIMESTAMP = True
