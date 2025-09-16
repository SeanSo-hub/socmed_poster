from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from fb_script import FacebookPoster
from twitter_script import TwitterPoster
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
    """Handle message posting with optional media for both Facebook and Twitter"""
    try:
        message = request.form.get('message', '').strip()
        platform = request.form.get('platform', 'facebook').strip()
        link = request.form.get('link', '').strip()
        
        success = False
        
        if platform == 'facebook':
            # Facebook posting logic
            poster = FacebookPoster()
            
            if not poster.verify_token() or not poster.verify_page_access():
                flash('Facebook authentication failed. Check your credentials.', 'error')
                return redirect(url_for('index'))
            
            poster.get_page_token()
            
            # Handle file upload for Facebook
            if 'media_file' in request.files and request.files['media_file'].filename != '':
                file = request.files['media_file']
                
                if file.content_type.startswith('image/') and allowed_file(file.filename, 'image'):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    success = poster.post_photo(filepath, message if message else None)
                    
                    try:
                        os.remove(filepath)
                    except:
                        pass
                        
                elif file.content_type.startswith('video/') and allowed_file(file.filename, 'video'):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    success = poster.post_video(filepath, message if message else None)
                    
                    try:
                        os.remove(filepath)
                    except:
                        pass
                else:
                    flash('Invalid file type for Facebook. Please upload an image or video file.', 'error')
                    return redirect(url_for('index'))
            else:
                # No file uploaded, post text message
                if not message:
                    flash('Please enter a message or upload a file!', 'error')
                    return redirect(url_for('index'))
                
                success = poster.post(message, link if link else None)
        
        elif platform == 'twitter':
            # Twitter posting logic
            poster = TwitterPoster()
            
            # Handle file upload for Twitter
            if 'media_file' in request.files and request.files['media_file'].filename != '':
                file = request.files['media_file']
                
                if (file.content_type.startswith('image/') and allowed_file(file.filename, 'image')) or \
                   (file.content_type.startswith('video/') and allowed_file(file.filename, 'video')):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    success = poster.post(message if message else "📎 Media post", [filepath])
                    
                    try:
                        os.remove(filepath)
                    except:
                        pass
                else:
                    flash('Invalid file type for Twitter. Please upload an image or video file.', 'error')
                    return redirect(url_for('index'))
            else:
                # No file uploaded, post text message
                if not message:
                    flash('Please enter a message!', 'error')
                    return redirect(url_for('index'))
                
                success = poster.post(message)
        
        else:
            flash('Invalid platform selected.', 'error')
            return redirect(url_for('index'))
        
        if success:
            platform_name = 'Facebook' if platform == 'facebook' else 'Twitter'
            flash(f'Content posted successfully to {platform_name}!', 'success')
        else:
            flash(f'Failed to post content to {platform}. Check console for details.', 'error')
            
    except ValueError as e:
        flash(f'Configuration error: {e}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """Check connection status for both platforms"""
    try:
        # Check Facebook status
        fb_poster = FacebookPoster()
        fb_token_valid = fb_poster.verify_token()
        fb_page_access = fb_poster.verify_page_access()
        
        fb_page_name = None
        if fb_page_access:
            page_result = fb_poster._request(fb_poster.page_id)
            if page_result:
                fb_page_name = page_result.get('name')
        
        # Check Twitter status
        try:
            tw_poster = TwitterPoster()
            # Try to authenticate to verify credentials
            tw_valid = bool(tw_poster.client and tw_poster.api)
        except:
            tw_valid = False
        
        return jsonify({
            'facebook': {
                'token_valid': fb_token_valid,
                'page_access': fb_page_access,
                'page_id': fb_poster.page_id,
                'page_name': fb_page_name
            },
            'twitter': {
                'credentials_valid': tw_valid
            }
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
