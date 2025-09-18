# SocMed Poster

A unified solution for posting to Facebook, Twitter, and Instagram with both web interface and command line support.

## 🚀 Features

- 📘 **Facebook Pages**: Text, images (up to 10), videos, and links
- 🐦 **Twitter**: Tweets with up to 4 media files (images/videos)
- 📸 **Instagram**: Image posts and carousels (up to 10 images, Business/Creator accounts)
- 🌐 **Web Interface**: Tailwind CSS UI with real-time platform status
- ⚡ **Auto-hiding Messages**: Success/error messages fade after 3 seconds
- 🔄 **Platform State Persistence**: UI remembers selected tab after posting
- 🛠️ **Command Line**: Direct posting scripts in `/scripts` folder
- 🔍 **Smart Diagnostics**: Platform-specific connection testing with `diagnose.py`
- 📊 **Dynamic UI**: Platform-specific media limits and character counts
- 🛡️ **Robust Error Handling**: Retry logic and graceful fallbacks

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
```

## 🌐 Web Interface

Open http://localhost:5000 after running `python app.py`

**Key Features:**

- 🎯 **Platform Tabs**: Switch between Facebook, Twitter, Instagram
- 📊 **Dynamic Limits**: Shows platform-specific media limits and character counts
- 🔄 **Real-time Status**: Connection indicators (🟡 checking, 🟢 connected, 🔴 failed)
- 📁 **Multi-upload**: Upload multiple files or paste URLs
- ⚡ **Auto-hide Messages**: Success/error notifications fade after 3 seconds
- 💾 **State Persistence**: Remembers selected platform after posting

**Character Limits:**

- Facebook: 63,206 characters
- Twitter: 280 characters
- Instagram: 2,200 characters

**Media Limits (displayed dynamically):**

- Facebook: Up to 10 images or 1 video per post
- Twitter: Up to 4 images/videos per tweet
- Instagram: Up to 10 images per carousel (images only)

## 🖥️ Command Line

All scripts are now organized in the `/scripts` folder:

```bash
python scripts/fb_script.py        # Facebook posting
python scripts/twitter_script.py   # Twitter posting
python scripts/instagram_script.py # Instagram posting
python diagnose.py                 # Test all platform connections
```

**Enhanced Features:**

- 🔄 **Retry Logic**: Automatic retries with backoff for failed requests
- 🛡️ **Error Handling**: Graceful fallbacks (Twitter v2 → v1.1 API)
- 📊 **Rich Logging**: Detailed connection and upload status

## 📋 Requirements

- Python 3.7+
- Facebook Page admin access
- Twitter Developer account
- Instagram Business/Creator account

## 🔧 Troubleshooting

- **Connection failed**: Check credentials and token expiration
- **Posts not appearing**: Verify platform policies and permissions
- **Upload issues**: Check file formats and size limits
- **Twitter ConnectionResetError**: Try again (automatic retries with v1.1 fallback)
- **Flask view errors**: Fixed in latest version (proper redirect handling)
- **Need detailed diagnosis**: Run `python diagnose.py` for comprehensive testing

**Diagnostic Features:**

- Internet connectivity test
- Platform API reachability
- Credential validation for all platforms
- Detailed error reporting with suggested fixes

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
