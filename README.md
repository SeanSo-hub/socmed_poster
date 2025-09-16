# SocMed Poster

A complete solution for posting text, images, and videos to both Facebook pages and Twitter with a unified web interface and command line options.

## 🚀 Features

### Multi-Platform Support

- 📘 **Facebook Pages**: Post to your Facebook business pages
- 🐦 **Twitter**: Post tweets with media attachments
- 🔄 **Platform Toggle**: Switch between platforms in the web interface

### Web Interface (Recommended)

- 🌐 **Clean Web UI**: Responsive interface for easy posting
- 📱 **Mobile Friendly**: Works on desktop, tablet, and mobile
- ✅ **Real-time Status**: Shows live connection status for both platforms
- 🔗 **Link Support**: Optional link attachment for Facebook posts
- 📊 **Smart Character Counter**: Facebook (63,206) and Twitter (280) limits
- 📂 **Smart Upload**: Upload any media file - automatically detects images or videos
- 🖼️ **Supported Images**: PNG, JPG, JPEG, GIF, WebP
- 🎬 **Supported Videos**: MP4, AVI, MOV, WMV, FLV, WebM, MKV
- 👁️ **Media Preview**: Preview images and videos before posting
- 🧹 **Auto Cleanup**: Temporary files are automatically deleted after posting

### Command Line Scripts

- 🖥️ **Terminal Access**: Direct execution from command line
- ⚡ **Fast Posting**: Quick posting without browser overhead
- 🤖 **Automation Ready**: Perfect for scripts and scheduled tasks
- 🔧 **Customizable**: Easy to modify for specific needs
- 📁 **Local Files**: Upload photos and videos from local filesystem

## 📦 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Credentials File

Create a `.env` file in the project directory with your API credentials:

```env
# Facebook API credentials
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here

# Twitter API credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET_KEY=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET_TOKEN=your_access_secret_here
```

**🔒 Security Warning**: Never commit the `.env` file to version control! Add it to your `.gitignore` file.

## 🌐 Web Interface Usage

### Starting the Web App

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

### Using the Interface

1. **Select Platform**: Choose Facebook or Twitter using the toggle buttons
2. **Check Status**: Verify the green connection indicator for your selected platform
3. **Enter Message**: Type your post content
   - Facebook: Up to 63,206 characters
   - Twitter: Up to 280 characters
4. **Upload Media** (optional):
   - Click "Choose File" to select image or video
   - Preview will show automatically
   - Twitter supports up to 4 media files
5. **Add Link** (Facebook only): Include a URL in your post
6. **Post**: Click the platform-specific post button
7. **Verify**: Check your social media platform to see the published post

### Platform-Specific Features

**Facebook:**

- Text + link posts
- Single image or video uploads
- Long-form content support
- Link previews

**Twitter:**

- Tweet threads (manual)
- Up to 4 media files per tweet
- Hashtag and mention support
- Character limit enforcement

## 🖥️ Command Line Usage

### Facebook Script

```bash
python fb_script.py
```

**What it does:**

- Verifies Facebook credentials automatically
- Attempts to upgrade to page access token
- Posts a test message
- Shows detailed status and error messages

### Twitter Script

```bash
python twitter_script.py
```

**What it does:**

- Verifies Twitter API credentials
- Posts a timestamped test tweet
- Includes retry logic for network issues
- Handles rate limiting automatically

### Diagnostic Tool

```bash
python diagnose.py
```

**What it does:**

- Tests internet connectivity
- Verifies API endpoints are reachable
- Validates credentials for both platforms
- Attempts test posts to verify functionality

### Customizing Posts

Edit the message in the respective scripts:

```python
# In fb_script.py
message = poster.post("Your custom Facebook message here!")

# In twitter_script.py
success = post_tweet("Your custom tweet here!")
```

### Adding Media Posts

**Facebook (fb_script.py):**

```python
# For photos
photo_success = poster.post_photo("./path/to/image.jpg", "Your photo caption")

# For videos
video_success = poster.post_video("./path/to/video.mp4", "Your video description")
```

**Twitter (twitter_script.py):**

```python
# Single media file
success = post_with_image("Your tweet text", "./path/to/image.jpg")
success = post_with_video("Your tweet text", "./path/to/video.mp4")

# Multiple media files
success = post_tweet("Your tweet text", ["./image1.jpg", "./image2.jpg"])
```

## 📁 Project Structure

```
python script/
├── app.py                 # Flask web application (main interface)
├── fb_script.py          # Facebook API client and CLI script
├── twitter_script.py     # Twitter API client and CLI script
├── diagnose.py           # Diagnostic tool for troubleshooting
├── templates/
│   └── index.html        # Web interface HTML template
├── uploads/              # Temporary file storage (auto-created)
├── .env                  # Your API credentials (create this)
├── .env.example          # Template for credentials (recommended)
├── requirements.txt      # Python dependencies
└── README.md            # This documentation
```

### Key Files Explained

- **`app.py`**: Flask web server with multi-platform support and file handling
- **`fb_script.py`**: Facebook Page posting with photo/video upload support
- **`twitter_script.py`**: Twitter posting with media uploads and retry logic
- **`diagnose.py`**: Comprehensive diagnostic tool for troubleshooting
- **`uploads/`**: Temporary directory for web interface file uploads
- **`.env`**: Your secret API credentials (not included in repository)

## 🔌 API Endpoints

The web interface provides these endpoints:

- `GET /` - Main posting interface with platform selection
- `POST /post` - Handle form submissions and file uploads for both platforms
- `GET /status` - JSON status check for both Facebook and Twitter connections
- `GET /health` - Simple health check endpoint

## 🔒 Security & Best Practices

### Credential Management

- **Environment Variables**: Keep all API credentials in `.env` file
- **Version Control**: Add `.env` to `.gitignore` - never commit credentials
- **Token Rotation**: Regularly regenerate access tokens for security
- **Least Privilege**: Use minimum required permissions for API access

### Facebook Security

- **Use Page Access Tokens**: Better permissions than user tokens
- **Admin Access**: Ensure you have admin access to target pages
- **App Permissions**: Verify `pages_manage_posts` and `pages_read_engagement` permissions

### Twitter Security

- **API v2**: Uses modern Twitter API with proper authentication
- **Rate Limiting**: Built-in rate limit handling and retry logic
- **Bearer Tokens**: Secure authentication without exposing credentials

### File Handling

- **Temporary Storage**: Uploaded files are deleted immediately after posting
- **File Validation**: Only supported image/video formats are accepted
- **Size Limits**: Respects platform guidelines for media uploads
- **Secure Filenames**: Uses `secure_filename()` to prevent path traversal

## 🔧 Troubleshooting

### Common Issues

**Platform Connection Failed**

- Check your `.env` file exists and has correct credentials for the selected platform
- Verify access tokens are valid and not expired
- For Facebook: Ensure you have admin access to the target page
- For Twitter: Verify all 4 API credentials are correctly set

**Authentication Failed**

- Regenerate expired tokens from respective developer consoles
- Facebook: Check `pages_manage_posts` and `pages_read_engagement` permissions
- Twitter: Verify API keys have read/write permissions
- Ensure credentials match the correct environment (sandbox vs production)

**Posts Not Appearing**

- Check platform community standards and posting policies
- Facebook: Verify page is published and not restricted
- Twitter: Check for duplicate content restrictions
- Some content may be under review by platform algorithms

**Web Interface Issues**

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is available or change it in `app.py`
- Clear browser cache and cookies
- Verify JavaScript is enabled for status checking

**File Upload Problems**

- Check file format is supported (see supported formats above)
- Ensure file size is under platform limits
- Twitter: Remember 4 media files maximum per tweet
- Verify file is not corrupted or protected

**Rate Limiting**

- Twitter: Built-in retry logic handles rate limits automatically
- Facebook: Reduce posting frequency if encountering limits
- Both: Wait for reset periods before retrying failed requests

### Getting Help

1. **Run Diagnostics**: Use `python diagnose.py` for comprehensive testing
2. **Check Terminal Output**: Detailed error messages help identify issues
3. **Platform Developer Consoles**:
   - Facebook: https://developers.facebook.com/
   - Twitter: https://developer.twitter.com/
4. **Test Incrementally**: Start with simple text posts before trying media
5. **Use Web Interface Status**: Real-time connection status helps debug issues

## 🎯 Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt    # Install all dependencies

# Web Interface
python app.py                      # Start web server (http://localhost:5000)

# Command Line - Facebook
python fb_script.py                # Post to Facebook
python fb_script.py main           # Alternative entry point

# Command Line - Twitter
python twitter_script.py           # Post to Twitter

# Diagnostics
python diagnose.py                 # Run comprehensive tests

# Testing Endpoints
curl http://localhost:5000/health  # Test web server health
curl http://localhost:5000/status  # Check platform connections
```

## 📋 Requirements

- **Python 3.7+**
- **Internet Connection**
- **Platform Access**:
  - Facebook Page Admin Access
  - Twitter Developer Account
- **Developer Apps**:
  - Facebook Developer App with appropriate permissions
  - Twitter Developer App with API v2 access

### Python Dependencies

- `flask>=2.3.0,<3.0.0` - Web framework for UI
- `requests>=2.31.0,<3.0.0` - HTTP requests to Facebook API
- `python-dotenv>=1.0.0,<2.0.0` - Environment variable management
- `tweepy>=4.14.0,<5.0.0` - Twitter API v2 client
- `werkzeug>=2.3.0,<3.0.0` - Secure file upload handling

## 🆕 Recent Updates

### Version 2.0 Features

- ✅ **Twitter Support**: Full Twitter integration with API v2
- ✅ **Updated Dependencies**: Added `tweepy` with proper version pinning
- ✅ **Enhanced UI**: Platform switching with real-time status
- ✅ **Improved Security**: Better credential management and file validation
- ✅ **Diagnostic Tools**: Comprehensive testing and troubleshooting
- ✅ **Better Error Handling**: Retry logic and detailed error messages
- ✅ **Multi-Media Support**: Enhanced media handling for both platforms

### Breaking Changes

- Old standalone scripts replaced with platform-specific modules
- `.env` file now requires Twitter credentials for full functionality
- Updated requirements.txt with new dependencies
