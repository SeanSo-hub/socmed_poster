# SocMed P## 🌐 **Web Interface**: Tailwind CSS UI with real-time platform status

- 🔍 **Smart Diagnostics**: Platform-specific connection testing with `diagnose.py`

## 🆕 Recent Updates

### ✅ **Instagram Upload Alignment**

- Unified file upload behavior across all platforms
- Instagram now accepts same image/video file types as Facebook/Twitter
- Consistent validation and error handling

### ✅ **LinkedIn Integration**

- Added professional LinkedIn posting support
- Text-only posts to personal profiles
- OAuth 2.0 authentication via LinkedIn Developer API
- Full diagnostic and API status checking

### ✅ **Self-Contained Package**

- Complete Python package with `pip install` support
- All dependencies and files included in package distribution
- Can be installed and run independently of source repository
- Module execution: `python -m socmed_poster`ter

A unified solution for posting to Facebook, Twitter, Instagram, and LinkedIn with both web interface and command line support.

## 🚀 Features

- 📘 **Facebook Pages**: Text, images (up to 10), videos, and links
- 🐦 **Twitter**: Tweets with up to 4 media files (images/videos)
- 📸 **Instagram**: Image posts and carousels (up to 10 images, Business/Creator accounts)
- 💼 **LinkedIn**: Professional text posts to personal profiles
- 🌐 **Web Interface**: Tailwind CSS UI with real-time platform status
- 🔍 **Smart Diagnostics**: Platform-specific connection testing with `diagnose.py`

## ⚙️ Quick Setup

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Create `.env` with your API credentials (see below)
3. **Run Web UI**: `python app.py` → Open http://localhost:5000
4. **Run CLI**: `python scripts/{platform}_script.py` for direct posting

## Project structure

```text
├── app.py                     # Flask application factory + startup
├── diagnose.py                # Multi-platform diagnostic utility
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .env                       # API credentials (create locally)
├── scripts/                   # Posting clients (Facebook, Twitter, Instagram, LinkedIn)
│   ├── fb_script.py
│   ├── twitter_script.py
│   ├── instagram_script.py
│   └── linkedin_script.py
├── routes/                    # Flask blueprints (UI and API)
│   ├── __init__.py
│   ├── main.py                # index & /post route
│   ├── api.py                 # /api/status and /api/health
│   └── utils.py               # public uploads + helpers
├── templates/                 # Jinja templates
│   ├── index.html
│   ├── _flash.html
│   └── _platform_tabs.html
├── static/                    # Static assets (JS/CSS)
│   └── js/app.js
└── uploads/                   # Temporary file storage (created at runtime)
```

Notes

- The frontend JS is in `static/js/app.js`. Templates include minimal inline config via `window.SOCMED_CONFIG`.
- Routes were refactored into `routes/` blueprints (main and api). Update references to endpoints if you rename blueprints.
- Use `diagnose.py` to validate credentials and network/API reachability.

If you want, I can run the app and perform a quick smoke test of `/` and `/api/status`.

## 📦 Package Installation & Distribution

This project is now a fully self-contained Python package that can be installed and distributed independently.

### Installation Options

**Option 1: Install as Package**

```bash
# Install in editable mode for development
pip install -e .

# Or build and install a wheel
python -m build
pip install dist/socmed_poster-*.whl
```

**Option 2: Run Directly**

```bash
# Traditional approach - run from source
python app.py
```

### Package Usage

**Run as a module:**

```bash
python -m socmed_poster
```

**Import in Python code:**

```python
import socmed_poster

# Create the Flask app
app = socmed_poster.create_app()

# Use individual components
from socmed_poster.scripts.fb_script import FacebookPoster
from socmed_poster.scripts.twitter_script import TwitterPoster
from socmed_poster.scripts.instagram_script import InstagramPoster
from socmed_poster.scripts.linkedin_script import LinkedInPoster

# Post to platforms
fb_poster = FacebookPoster()
fb_poster.post("Hello from Facebook!")

li_poster = LinkedInPoster()
li_poster.post("Hello from LinkedIn!")
```

**Key Package Features:**

- ✅ **Self-contained**: All scripts, templates, and static files included
- ✅ **Pip installable**: Standard Python package with `pyproject.toml`
- ✅ **Module execution**: Run with `python -m socmed_poster`
- ✅ **Import support**: Use components individually in your code
- ✅ **No external dependencies**: Package includes all necessary files

## As a Python package

You can use this repository as an importable package. From the repository root you can:

- Install in editable mode for development:

```powershell
pip install -e .
```

- Run the web UI as a module:

```powershell
python -m socmed_poster
```

Or import the app factory in Python:

```py
from socmed_poster import create_app
app = create_app()
```
