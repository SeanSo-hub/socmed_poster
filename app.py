from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from post_script import FacebookPoster
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, file_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS[file_type]

@app.route('/')
def index():
    """Main page with posting form"""
    return render_template('index.html')

@app.route('/post', methods=['POST'])
def post_message():
    """Handle message posting with optional media"""
    try:
        message = request.form.get('message', '').strip()
        link = request.form.get('link', '').strip()
        
        # Create poster and verify credentials
        poster = FacebookPoster()
        
        if not poster.verify_token() or not poster.verify_page_access():
            flash('Authentication failed. Check your credentials.', 'error')
            return redirect(url_for('index'))
        
        # Try to get page token
        poster.get_page_token()
        
        success = False
        
        # Check if a file was uploaded
        if 'media_file' in request.files and request.files['media_file'].filename != '':
            file = request.files['media_file']
            
            # Determine file type and process accordingly
            if file.content_type.startswith('image/') and allowed_file(file.filename, 'image'):
                # Handle image upload
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                success = poster.post_photo(filepath, message if message else None)
                
                # Clean up uploaded file
                try:
                    os.remove(filepath)
                except:
                    pass
                    
            elif file.content_type.startswith('video/') and allowed_file(file.filename, 'video'):
                # Handle video upload
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                success = poster.post_video(filepath, message if message else None)
                
                # Clean up uploaded file
                try:
                    os.remove(filepath)
                except:
                    pass
            else:
                flash('Invalid file type. Please upload an image or video file.', 'error')
                return redirect(url_for('index'))
        else:
            # No file uploaded, post text message
            if not message:
                flash('Please enter a message or upload a file!', 'error')
                return redirect(url_for('index'))
            
            success = poster.post(message, link if link else None)
        
        if success:
            flash('Content posted successfully!', 'success')
        else:
            flash('Failed to post content. Check console for details.', 'error')
            
    except ValueError as e:
        flash(f'Configuration error: {e}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """Check connection status"""
    try:
        poster = FacebookPoster()
        token_valid = poster.verify_token()
        page_access = poster.verify_page_access()
        
        # Get page name if we have access
        page_name = None
        if page_access:
            page_result = poster._request(poster.page_id)
            if page_result:
                page_name = page_result.get('name')
        
        return jsonify({
            'token_valid': token_valid,
            'page_access': page_access,
            'page_id': poster.page_id,
            'page_name': page_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Simple health check"""
    return jsonify({'status': 'healthy', 'service': 'Facebook Poster'})

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found! Create one with your Facebook credentials.")
        exit(1)
    
    print("🚀 Starting Facebook Poster Web UI...")
    print("📱 Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
