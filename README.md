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

### Required Credentials (.env)

```env
# Facebook
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_token

# Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET_KEY=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET_TOKEN=your_secret

# Instagram (Business account required)
INSTAGRAM_USER_ID=your_user_id
INSTAGRAM_ACCESS_TOKEN=your_token

# Optional: For Instagram local uploads
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_UPLOAD_PRESET=your_preset

## 📁 Project Structure

```
├── app.py                 # Flask web interface
├── diagnose.py            # Multi-platform diagnostic tool
├── requirements.txt       # Python dependencies
├── .env                   # API credentials (create this)
├── scripts/               # Platform-specific posting modules
│   ├── fb_script.py       # Facebook Graph API client
│   ├── twitter_script.py  # Twitter API client (v2 + v1.1 fallback)
│   └── instagram_script.py # Instagram Graph API client
├── templates/
│   └── index.html         # Web UI with dynamic features
└── uploads/               # Temporary file storage
```

## 🆕 Recent Updates

- ✅ **Fixed Flask view return errors** - Proper redirect handling after posts
- ✅ **Auto-hiding flash messages** - Success/error messages fade after 3 seconds
- ✅ **Dynamic media limits** - Platform-specific upload limits shown in UI
- ✅ **Enhanced Twitter reliability** - Retry logic + v1.1 API fallback
- ✅ **Organized code structure** - All posting scripts moved to `/scripts` folder
- ✅ **Improved diagnostics** - Comprehensive connection testing in `diagnose.py`
