# SocMed Poster

A unified solution for posting to Facebook, Twitter, and Instagram with both web interface and command line support.

## 🚀 Features

- 📘 **Facebook Pages**: Text, images (up to 10), videos, and links
- 🐦 **Twitter**: Tweets with up to 4 media files (images/videos)
- 📸 **Instagram**: Image posts and carousels (up to 10 images, Business/Creator accounts)
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
├── scripts/                   # Posting clients (Facebook, Twitter, Instagram)
│   ├── fb_script.py
│   ├── twitter_script.py
│   └── instagram_script.py
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
