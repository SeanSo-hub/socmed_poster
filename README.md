# SocMed Poster

A unified solution for posting to Facebook, Twitter, and Instagram with both web interface and command line support.

## 🚀 Features

- 📘 **Facebook Pages**: Text, images, videos, and links
- 🐦 **Twitter**: Tweets with up to 4 media files
- 📸 **Instagram**: Image posts (Business/Creator accounts)
- � **Web Interface**: Tailwind CSS UI with real-time status
- �️ **Command Line**: Direct posting scripts
- � **Smart Status**: Platform-specific connection checking

## � Quick Setup

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Create `.env` with your API credentials
3. **Run**: `python app.py` (web) or `python {platform}_script.py` (CLI)

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

- Switch platforms with tabs
- Real-time connection status (🟡 checking, 🟢 connected, 🔴 failed)
- Upload media files or paste URLs
- Character limits: Facebook (63K), Twitter (280), Instagram (2.2K)

## 🖥️ Command Line

```bash
python fb_script.py        # Facebook posting
python twitter_script.py   # Twitter posting
python instagram_script.py # Instagram posting
python diagnose.py         # Test all connections
```

## 📋 Requirements

- Python 3.7+
- Facebook Page admin access
- Twitter Developer account
- Instagram Business/Creator account

## � Troubleshooting

- **Connection failed**: Check credentials and token expiration
- **Posts not appearing**: Verify platform policies and permissions
- **Upload issues**: Check file formats and size limits
- **Need help**: Run `python diagnose.py` for detailed testing

## 📁 Files

- `app.py` - Web interface
- `fb_script.py` - Facebook client
- `twitter_script.py` - Twitter client
- `instagram_script.py` - Instagram client
- `templates/index.html` - Web UI
