# SocMed Poster

A complete solution for posting text, images, and videos to Facebook pages with both web interface and command line options.

## 🚀 Three Ways to Use

### Option 1: Web Interface (Recommended)

- 🌐 **Web Interface**: Clean, responsive UI for posting messages
- 📱 **Mobile Friendly**: Works on desktop and mobile devices
- ✅ **Real-time Status**: Shows connection status to Facebook
- 🔗 **Link Support**: Optional link attachment to posts
- 📊 **Character Counter**: Shows remaining characters (63,206 limit)
- � **Smart Upload**: Upload any media file - automatically detects and posts images or videos
- 🖼️ **Supported Images**: PNG, JPG, JPEG, GIF, WebP
- 🎬 **Supported Videos**: MP4, AVI, MOV, WMV, FLV, WebM, MKV
- 👁️ **Media Preview**: Preview images and videos before posting

### Option 2: Post Script (Main CLI)

- 🖥️ **Command Line**: Direct execution from terminal
- ⚡ **Fast**: Quick posting without browser
- 🤖 **Automation**: Perfect for scripts and automation
- 🔧 **Customizable**: Easy to modify for specific needs
- 🖼️ **Media Support**: Upload photos and videos via code
- 📁 **File Handling**: Supports local file uploads

### Option 3: Standalone Script (Independent)

- 🎯 **Self-contained**: Independent version with built-in posting logic
- 🔄 **Consistent**: Same functionality as post_script.py but standalone
- 📦 **Portable**: Can be used independently without other files
- 🖼️ **Media Support**: Full photo and video upload capabilities

- 🌐 **Web Interface**: Clean, responsive UI for posting messages
- 📱 **Mobile Friendly**: Works on desktop and mobile devices
- ✅ **Real-time Status**: Shows connection status to Facebook
- 🔗 **Link Support**: Optional link attachment to posts
- 📊 **Character Counter**: Shows remaining characters (63,206 limit)

### Option 2: Post Script

- 🖥️ **Command Line**: Direct execution from terminal
- ⚡ **Fast**: Quick posting without browser
- 🤖 **Automation**: Perfect for scripts and automation
- 🔧 **Customizable**: Easy to modify for specific needs

### Option 3: Standalone Script

- 🎯 **Self-contained**: Independent version with built-in posting logic
- 🔄 **Consistent**: Same functionality as post_script.py but standalone
- 📦 **Portable**: Can be used independently without other files

A complete solution for posting messages to Facebook pages with both web interface and standalone script options.

## 🚀 Two Ways to Use

### Option 1: Web Interface (Recommended)

- 🌐 **Web Interface**: Clean, responsive UI for posting messages
- 📱 **Mobile Friendly**: Works on desktop and mobile devices
- ✅ **Real-time Status**: Shows connection status to Facebook
- 🔗 **Link Support**: Optional link attachment to posts
- 📊 **Character Counter**: Shows remaining characters (63,206 limit)

### Option 2: Standalone Script

- �️ **Command Line**: Direct execution from terminal
- ⚡ **Fast**: Quick posting without browser
- 🤖 **Automation**: Perfect for scripts and automation
- 🔧 **Customizable**: Easy to modify for specific needs

## 📦 Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file** with your Facebook credentials:

   ```env
   FACEBOOK_PAGE_ID=your_page_id_here
   FACEBOOK_ACCESS_TOKEN=your_access_token_here
   ```

## 🌐 Web Interface Usage

1. **Run the web application**:

   ```bash
   python app.py
   ```

2. **Open your browser** to: http://localhost:5000

3. **Use the interface**:
   - Check that the connection status shows "Connected to Facebook"
   - Select post type: Text, Photo, or Video
   - For text posts: Type your message and optionally add a link
   - For photo posts: Select an image file and add an optional caption
   - For video posts: Select a video file and add an optional description
   - Preview your media before posting
   - Click "Post to Facebook"
   - Check your Facebook page to see the post

## 🖥️ Command Line Script Usage

### Post Script (Recommended for CLI)

1. **Run the post script**:

   ```bash
   python post_script.py
   ```

2. **What it does**:

   - Automatically verifies your Facebook credentials
   - Attempts to get page access token for better permissions
   - Posts a test message to your Facebook page
   - Shows success/failure status

3. **Customize the message**:
   Edit line 94 in `post_script.py`:

   ```python
   success = poster.post("Your custom message here! 🚀")
   ```

4. **To post media** (uncomment these lines):

   ```python
   # For photos
   photo_success = poster.post_photo("./path/to/image.jpg", "Your caption")

   # For videos
   video_success = poster.post_video("./path/to/video.mp4", "Your description")
   ```

### Standalone Script (Alternative)

1. **Run the standalone script**:

   ```bash
   python standalone_script.py
   ```

2. **What it does**:

   - Self-contained version with identical functionality
   - Posts "Test for standalone script!" message
   - Independent of other project files

3. **Customize the message**:
   Edit line 104 in `standalone_script.py`:

   ```python
   message = poster.post("Your custom standalone message!")
   ```

4. **To post media** (uncomment these lines):

   ```python
   # For photos
   photo_success = poster.post_photo("./test_image.jpg", "Test photo caption")

   # For videos
   video_success = poster.post_video("./test_video.mp4", "Test video description")
   ```

## 📁 File Structure

```
python script/
├── app.py                 # Flask web application
├── post_script.py         # Main Facebook posting script
├── standalone_script.py   # Self-contained posting script
├── templates/
│   └── index.html         # Web interface template
├── uploads/               # Temporary upload directory (auto-created)
├── .env                   # Your credentials (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔌 API Endpoints (Web Interface)

- `GET /` - Main web interface
- `POST /post` - Submit a new post
- `GET /status` - Check connection status (JSON)
- `GET /health` - Health check endpoint

## Usage

### Web Interface:

1. Open the web interface in your browser
2. Check that the connection status shows "Connected to Facebook"
3. Type your message in the text area
4. Optionally add a link
5. Click "Post to Facebook"
6. Check your Facebook page to see the post

### Command Line Scripts:

1. **Post Script**: Run `python post_script.py`
2. **Standalone Script**: Run `python standalone_script.py`
3. Both scripts automatically handle authentication and posting
4. Check terminal output for success/failure status
5. Customize messages by editing the respective script files

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use page access tokens for better permissions
- Revoke tokens immediately if they're compromised
- Both web interface and standalone script use the same secure credential system

## 🔧 Troubleshooting

- **"Connection failed"**: Check your `.env` file and token permissions
- **"Authentication failed"**: Your token may be expired or invalid
- **Posts not appearing**: Check Facebook's posting policies and page settings
- **Web interface not loading**: Make sure Flask is installed (`pip install flask`)
- **Standalone script errors**: Run `python post_script.py` and check error messages

## 🎯 Quick Commands

```bash
# Web Interface
python app.py                      # Start web server
# Then open: http://localhost:5000

# Command Line Scripts
python post_script.py              # Main posting script
python standalone_script.py        # Alternative standalone version

# Setup
pip install -r requirements.txt    # Install all dependencies
```
