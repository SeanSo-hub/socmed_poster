# SocMed Poster

## 🌐 **Web Interface**: Tailwind CSS UI with real-time platform status

🔍 **Smart Diagnostics**: Platform-specific connection testing with `diagnose.py`

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

## ⚙️ Quick start

1. Install dependencies (choose one):

```powershell
# Quick (install runtime deps)
pip install -r requirements.txt

# OR for development (editable install)
pip install -e .
```

2. Configure credentials:

```powershell
copy .env.example .env
# Edit .env and add your API keys (e.g. LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID)
```

3. Run the app:

```powershell
# Run from source
python app.py

# Or run as an installed module
python -m socmed_poster
```

4. Test platform APIs or post directly with the helper scripts:

```powershell
python .\scripts\test_linkedin.py    # requires LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID
python .\scripts\instagram_script.py
```

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
- For LinkedIn debugging, prefer `scripts/test_linkedin.py` (posts using `LINKEDIN_PERSON_ID`) or run the Authorization Code flow and call `/me` once to discover the numeric id.

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

Run as a module (when installed):

```powershell
python -m socmed_poster
```

Import in Python code (example):

```python
from socmed_poster import create_app
app = create_app()

# Use individual components
from scripts.linkedin_script import LinkedInPoster

# When creating LinkedInPoster, provide LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID in env
li_poster = LinkedInPoster()
li_poster.post("Hello from LinkedIn!")
```

Key package notes:

- ✅ **Self-contained**: All scripts, templates, and static files are included in the project
- ✅ **Pip installable**: Standard Python package metadata is present (`pyproject.toml`)
- ✅ **Module execution**: Run with `python -m socmed_poster` after install
- ⚠️ **Dependencies**: Install required Python packages via `requirements.txt` or `pip install -e .` before running

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
