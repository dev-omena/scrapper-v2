# Google Maps Scraper

A powerful Python-based web scraper designed to extract business information from Google Maps search results. This tool provides a user-friendly GUI interface and can export data in multiple formats including Excel, CSV, and JSON.

## 🚀 Features

### Core Functionality
- **Automated Google Maps Scraping**: Automatically scrolls through search results and extracts business data
- **Multi-format Export**: Save data in Excel (.xlsx), CSV (.csv), or JSON (.json) formats
- **Headless Mode**: Option to run the browser in headless mode for server environments
- **Real-time Progress**: Live updates during the scraping process
- **Error Handling**: Robust error handling with detailed error codes

### Data Extraction Capabilities
The scraper extracts the following business information:
- **Business Name**: Full business name
- **Category**: Business category/type
- **Address**: Complete business address
- **Phone Number**: Contact phone number
- **Website**: Business website URL
- **Email**: Email addresses extracted from business websites
- **Rating**: Google Maps rating (stars)
- **Total Reviews**: Number of reviews
- **Business Hours**: Operating hours
- **Business Status**: Open/Closed status
- **Google Maps URL**: Direct link to the business on Google Maps
- **Booking Links**: Online booking/reservation links

### Technical Features
- **Undetected Chrome Driver**: Uses undetected-chromedriver to avoid detection
- **Smart Scrolling**: Automatically scrolls to load all available results
- **Email Extraction**: Intelligently extracts email addresses from business websites
- **Thread-safe Operations**: Multi-threaded architecture for smooth UI experience
- **Configurable Settings**: Customizable output paths and driver settings

## 📋 Requirements

- Python 3.7 or higher
- Chrome browser installed on your system
- Internet connection

## 🛠️ Installation

### Quick Setup (Recommended)

#### For Windows:
```cmd
# Run the setup script
setup_win.cmd
```

#### For Linux:
```bash
# Make the script executable and run it
chmod +x setup_linux.sh
./setup_linux.sh
```

### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Google-Maps-Scraper
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Local Usage

1. **Run the main application:**
   ```bash
   python app/run.py
   ```

2. **Using the GUI:**
   - Enter your search query (e.g., "restaurants in New York")
   - Select output format (Excel, CSV, or JSON)
   - Optionally enable headless mode
   - Click "Submit" to start scraping

### Railway Deployment (Team Access)

1. **Quick Deployment:**
   ```bash
   python deploy_railway.py
   ```

2. **Manual Deployment:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

3. **Access Web Interface:**
   - Open your Railway URL in browser
   - Use the modern web interface
   - All scraping runs in headless mode
   - Download results automatically

### Configuration

Edit `app/settings.py` to customize settings:

```python
# Output directory for scraped data
OUTPUT_PATH = "output/"

# Custom Chrome driver path (optional)
DRIVER_EXECUTABLE_PATH = None
```

## 📁 Project Structure

```
Google-Maps-Scraper/
├── app/
│   ├── images/                 # GUI images and icons
│   ├── scraper/               # Core scraping modules
│   │   ├── base.py           # Base class with common functionality
│   │   ├── scraper.py        # Main scraper backend
│   │   ├── frontend.py       # GUI interface
│   │   ├── parser.py         # HTML parsing and data extraction
│   │   ├── scroller.py       # Auto-scrolling functionality
│   │   ├── datasaver.py      # Data saving utilities
│   │   ├── communicator.py   # Frontend-backend communication
│   │   ├── common.py         # Shared utilities
│   │   └── error_codes.py    # Error code definitions
│   ├── run.py                # Application entry point
│   └── settings.py           # Configuration settings
├── output/                    # Default output directory
├── requirements.txt           # Python dependencies
├── setup_win.cmd             # Windows setup script
├── setup_linux.sh           # Linux setup script
└── README.md                 # This file
```

## 🔧 Dependencies

The project uses the following key dependencies:

- **selenium**: Web automation framework
- **undetected-chromedriver**: Chrome driver that bypasses detection
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and export
- **requests**: HTTP requests for email extraction
- **tkinter**: GUI framework (built-in with Python)

## 📊 Output Data Format

The scraper generates files with the following structure:

| Field | Description |
|-------|-------------|
| Category | Business category/type |
| Name | Business name |
| Phone | Contact phone number |
| Google Maps URL | Direct link to business on Google Maps |
| Website | Business website URL |
| Email | Extracted email addresses |
| Business Status | Open/Closed status |
| Address | Complete business address |
| Total Reviews | Number of Google reviews |
| Booking Links | Online booking/reservation links |
| Rating | Google Maps rating |
| Hours | Operating hours |

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues:**
   - Ensure Chrome browser is installed
   - The application will automatically download the appropriate ChromeDriver

2. **No Results Found:**
   - Verify your search query is valid
   - Check your internet connection
   - Try different search terms

3. **Permission Errors:**
   - Ensure you have write permissions in the output directory
   - Run as administrator if necessary (Windows)

### Error Codes

- `ds0`: No records to save
- `pp0`: Error while parsing business details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Railway Deployment

### Quick Team Deployment

For team access, deploy to Railway:

```bash
# Automated deployment
python deploy_railway.py

# Or manual deployment
npm install -g @railway/cli
railway login
railway init
railway up
```

### Railway Features

- **Web Interface**: Modern, responsive web UI
- **Headless Mode**: Runs Chrome in background
- **Team Access**: Share URL with your team
- **Auto Downloads**: Files download automatically
- **Real-time Updates**: Live progress monitoring
- **Health Checks**: Built-in monitoring

### Railway vs Local

| Feature | Local | Railway |
|---------|-------|---------|
| GUI Interface | ✅ Tkinter | ✅ Web UI |
| Headless Mode | Optional | Required |
| Team Access | ❌ Single user | ✅ Multiple users |
| Setup Complexity | Low | Medium |
| Maintenance | Manual | Automated |

## 📚 Additional Resources

- [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md) - Detailed Railway setup
- [Railway Documentation](https://docs.railway.app) - Official Railway docs
- [Chrome Headless Guide](https://developers.google.com/web/updates/2017/04/headless-chrome) - Chrome headless info

## 🙏 Acknowledgments

- Built with Python and Selenium
- Uses undetected-chromedriver for stealth scraping
- GUI powered by tkinter
- Data processing with pandas
- Web interface powered by Flask

---

**Note**: This tool is for educational and research purposes. Please respect Google's Terms of Service and use responsibly. The developers are not responsible for any misuse of this tool.
