# SocMed Poster

A complete solution for posting text, images, and videos to Facebook pages with both web interface and command line options.

## 🚀 Two Ways to Use

### Option 1: Web Interface (Recommended)

- 🌐 **Clean Web UI**: Responsive interface for easy posting
- 📱 **Mobile Friendly**: Works on desktop, tablet, and mobile
- ✅ **Real-time Status**: Shows live connection status to Facebook
- 🔗 **Link Support**: Optional link attachment to posts
- 📊 **Character Counter**: Shows remaining characters (63,206 limit)
- 📂 **Smart Upload**: Upload any media file - automatically detects images or videos
- 🖼️ **Supported Images**: PNG, JPG, JPEG, GIF, WebP
- 🎬 **Supported Videos**: MP4, AVI, MOV, WMV, FLV, WebM, MKV
- 👁️ **Media Preview**: Preview images and videos before posting
- 🧹 **Auto Cleanup**: Temporary files are automatically deleted after posting

### Option 2: Command Line Scripts

- 🖥️ **Terminal Access**: Direct execution from command line
- ⚡ **Fast Posting**: Quick posting without browser overhead
- 🤖 **Automation Ready**: Perfect for scripts and scheduled tasks
- 🔧 **Customizable**: Easy to modify for specific needs
- 📁 **Local Files**: Upload photos and videos from local filesystem
- 🔄 **Two Options**: Main script and standalone script (nearly identical)

## 📦 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Credentials File

Create a `.env` file in the project directory:

```env
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
```

**Important**: Never commit the `.env` file to version control!

## 🌐 Web Interface Usage

### Starting the Web App

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

### Using the Interface

1. **Check Status**: Verify the green "Connected to Facebook Page" indicator
2. **Enter Message**: Type your post content (optional if uploading media)
3. **Upload Media** (optional): 
   - Click "Choose File" to select image or video
   - Preview will show automatically
4. **Add Link** (optional): Include a URL in your post
5. **Post**: Click "📤 Post to Facebook"
6. **Verify**: Check your Facebook page to see the published post

### Supported Actions

- **Text Only**: Just enter a message and post
- **Image Post**: Upload image with optional caption
- **Video Post**: Upload video with optional description
- **Mixed Content**: Text + image/video + link combination

## 🖥️ Command Line Usage

### Main Script

```bash
python post_script.py
```

**What it does:**
- Verifies Facebook credentials automatically
- Attempts to upgrade to page access token
- Posts a test message: "Another test post! with improvements"
- Shows detailed status and error messages

### Standalone Script

```bash
python standalone_script.py
```

**What it does:**
- Same functionality as main script
- Posts: "Test for standalone script!"
- Includes commented examples for media uploads

### Customizing Posts

Edit the message in either script:

```python
# In post_script.py (line 148)
message = poster.post("Your custom message here!")

# In standalone_script.py (line 148)  
message = poster.post("Your custom message here!")
```

### Adding Media Posts

Uncomment and modify these lines in either script:

```python
# For photos
photo_success = poster.post_photo("./path/to/image.jpg", "Your photo caption")

# For videos
video_success = poster.post_video("./path/to/video.mp4", "Your video description")
```

## 📁 Project Structure

```
python script/
├── app.py                 # Flask web application
├── post_script.py         # Main CLI posting script
├── standalone_script.py   # Alternative CLI script (nearly identical)
├── templates/
│   └── index.html         # Web interface HTML template
├── uploads/               # Temporary file storage (auto-created)
├── .env                   # Your Facebook credentials (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This documentation
```

### Key Files Explained

- **`app.py`**: Flask web server with upload handling and automatic file cleanup
- **`post_script.py`**: Main command line script with full functionality
- **`standalone_script.py`**: Nearly identical to post_script.py (only differs in test message)
- **`uploads/`**: Temporary directory where web uploads are stored briefly before posting and deletion
- **`.env`**: Your secret Facebook credentials (not included in repository)

## 🔌 API Endpoints

The web interface provides these endpoints:

- `GET /` - Main posting interface
- `POST /post` - Handle form submissions and file uploads
- `GET /status` - JSON status check for connection health
- `GET /health` - Simple health check endpoint

## 🔒 Security & Best Practices

### Token Management
- **Use Page Access Tokens**: Better permissions than user tokens
- **Token Rotation**: Regularly regenerate access tokens
- **Environment Variables**: Never hardcode tokens in source code
- **Git Safety**: `.env` files should be in `.gitignore`

### File Handling
- **Temporary Storage**: Uploaded files are deleted immediately after posting
- **File Validation**: Only supported image/video formats are accepted
- **Size Limits**: Follow Facebook's guidelines for media uploads

## 🔧 Troubleshooting

### Common Issues

**Connection Failed**
- Check your `.env` file exists and has correct credentials
- Verify your Facebook access token is valid and not expired
- Ensure you have admin access to the target Facebook page

**Authentication Failed**
- Your token may be expired - generate a new one
- Check if your app has `pages_manage_posts` and `pages_read_engagement` permissions
- Verify the page ID is correct

**Posts Not Appearing**
- Check Facebook's community standards and posting policies
- Verify your page is published and not restricted
- Some content may be under review by Facebook

**Web Interface Issues**
- Ensure Flask is installed: `pip install flask`
- Check if port 5000 is available or change it in `app.py`
- Clear browser cache and cookies

**File Upload Problems**
- Check file format is supported (see supported formats above)
- Ensure file size is under limits
- Verify file is not corrupted

### Getting Help

1. Check terminal output for detailed error messages
2. Verify your Facebook Developer Console for app status
3. Test with small files first before uploading large videos
4. Use the web interface's status indicator to verify connection

## 🎯 Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt    # Install dependencies

# Web Interface
python app.py                      # Start web server (http://localhost:5000)

# Command Line
python post_script.py              # Main CLI script
python standalone_script.py        # Alternative CLI script

# Testing
curl http://localhost:5000/health  # Test web server health
curl http://localhost:5000/status  # Check Facebook connection
```

## 📋 Requirements

- **Python 3.7+**
- **Internet Connection**
- **Facebook Page Admin Access**
- **Facebook Developer App** with appropriate permissions

### Python Dependencies

- `requests` - HTTP requests to Facebook API
- `python-dotenv` - Environment variable management  
- `flask` - Web framework for UI
- `werkzeug` - Secure file upload handling