# Social Media Poster - Self-Contained Package

This directory contains a **complete, self-contained** version of the Social Media Poster application that supports Facebook, Twitter, Instagram, and LinkedIn posting.

## 🎯 What's Included

This package contains everything needed to run the Social Media Poster:

- ✅ **Complete Python package** (`socmed_poster/`)
- ✅ **Four social platforms** (Facebook, Twitter, Instagram, LinkedIn)
- ✅ **All dependencies specified** (`pyproject.toml`)
- ✅ **Documentation** (`README.md`)
- ✅ **Configuration template** (`.env.example`)
- ✅ **Installation script** (`install.py`)
- ✅ **Distribution files** (`MANIFEST.in`, `setup.cfg`)

## 🚀 Quick Start

### Option 1: Automated Installation

```bash
python install.py
```

### Option 2: Manual Installation

```bash
# Install the package
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your API credentials
# Then run the application
python -m socmed_poster
```

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Social media API credentials (Facebook, Twitter, Instagram)

## 🔧 Configuration

1. **Copy the environment template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your API credentials:**

   ```env
   FACEBOOK_PAGE_ID=your_page_id
   FACEBOOK_ACCESS_TOKEN=your_access_token
   TWITTER_API_KEY=your_api_key
   # ... etc
   ```

3. **Get API credentials:**
   - **Facebook:** [Facebook Developers](https://developers.facebook.com/)
   - **Twitter:** [Twitter Developer Portal](https://developer.twitter.com/)
   - **Instagram:** [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api/)
   - **LinkedIn:** [LinkedIn Developer Portal](https://developer.linkedin.com/)

## 🌐 Usage

After installation, run:

```bash
python -m socmed_poster
```

Then open http://localhost:5000 in your browser.

## 📦 Distribution

This directory can be:

- Zipped and shared directly
- Uploaded to a private repository
- Published to PyPI
- Distributed as a standalone package

## 🆘 Support

If you encounter issues:

1. Check that all dependencies are installed: `pip list`
2. Verify your .env file has valid API credentials
3. Check the console output for specific error messages

## 📁 Directory Structure

```
socmed_poster/
├── socmed_poster/          # Main package code
│   ├── scripts/           # Social media API clients
│   ├── routes/            # Flask web routes
│   ├── templates/         # HTML templates
│   ├── static/            # CSS/JS assets
│   └── ...
├── pyproject.toml         # Package configuration
├── README.md              # This file
├── .env.example           # Environment template
├── install.py             # Installation script
└── ...
```

---

**Note:** This is a self-contained distribution. You don't need the original repository to use this package.
