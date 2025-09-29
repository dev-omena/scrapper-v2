# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Install system dependencies for Chrome and GUI
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxtst6 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Flask for web interface
RUN pip install flask==2.3.3

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Set environment variables for Railway
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV PORT=8000

# Create startup script for Railway
RUN echo '#!/bin/bash\n\
echo "Starting Xvfb for headless Chrome..."\n\
Xvfb :99 -screen 0 1920x1080x24 &\n\
sleep 2\n\
echo "Starting Flask application..."\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# Expose port for Railway
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Railway-specific startup command
CMD ["/start.sh", "python", "app/railway_app.py"]
