from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
from fb_script import FacebookPoster
from twitter_script import TwitterPoster
from instagram_script import InstagramPoster
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
os.makedirs(os.path.join(UPLOAD_FOLDER, 'public'), exist_ok=True)

# Public uploads route (files placed in uploads/public will be served here)
@app.route('/public_uploads/<path:filename>')
def public_upload(filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'public'), filename)

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
        
        elif platform == 'instagram':
            try:
                ig = InstagramPoster()
                # Print verification to terminal
                print(f"✅ Instagram poster initialized for IG ID {ig.ig_id}")

                # If a file was uploaded via the form, save it and pass local path to poster
                if 'media_file' in request.files and request.files['media_file'].filename != '':
                    file = request.files['media_file']
                    if file.content_type.startswith('image/') and allowed_file(file.filename, 'image'):
                        filename = secure_filename(file.filename)
                        temp_dir = os.path.join(UPLOAD_FOLDER, 'temp')
                        os.makedirs(temp_dir, exist_ok=True)
                        filepath = os.path.join(temp_dir, filename)
                        file.save(filepath)
                        print(f"📁 Saved temporary upload: {filepath}")
                        # Let InstagramPoster handle uploading to Cloudinary if configured.
                        result = ig.post_image(filepath, message if message else '')
                        try:
                            os.remove(filepath)
                        except:
                            pass
                        success = bool(result)
                    else:
                        flash('Invalid file type for Instagram. Please upload an image file.', 'error')
                        return redirect(url_for('index'))
                else:
                    # Use 'link' form field as image URL
                    if not link or not link.startswith('http'):
                        flash('Please provide a publicly accessible image URL in the link field for Instagram posts.', 'error')
                        return redirect(url_for('index'))
                    result = ig.post_image(link, message if message else '')
                    success = bool(result)
            except ValueError as e:
                flash(f'Configuration error: {e}', 'error')
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Instagram error: {e}")
                flash('Failed to post to Instagram. Check console for details.', 'error')
                return redirect(url_for('index'))

        else:
            flash('Invalid platform selected.', 'error')
            return redirect(url_for('index'))
        
        if success:
            if platform == 'facebook':
                platform_name = 'Facebook'
            elif platform == 'twitter':
                platform_name = 'Twitter'
            elif platform == 'instagram':
                platform_name = 'Instagram'
            else:
                platform_name = platform.title()
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
    """Check connection status for platforms"""
    # Get platform parameter (optional - if not provided, check all)
    platform = request.args.get('platform', '').lower()
    
    result = {}
    
    try:
        if platform == 'facebook' or not platform:
            print("🔍 Status check requested for Facebook")
            try:
                fb_poster = FacebookPoster()
                fb_token_valid = fb_poster.verify_token()
                fb_page_access = fb_poster.verify_page_access() if fb_token_valid else False
                
                fb_page_name = None
                if fb_page_access:
                    page_result = fb_poster._request(fb_poster.page_id)
                    if page_result:
                        fb_page_name = page_result.get('name')
                
                result['facebook'] = {
                    'token_valid': fb_token_valid,
                    'page_access': fb_page_access,
                    'page_id': fb_poster.page_id,
                    'page_name': fb_page_name
                }
            except Exception as e:
                print(f"❌ Facebook status check failed: {e}")
                result['facebook'] = {
                    'token_valid': False,
                    'page_access': False,
                    'error': str(e)
                }
        
        if platform == 'twitter' or not platform:
            print("🔍 Status check requested for Twitter")
            try:
                tw_poster = TwitterPoster()
                tw_valid = tw_poster.verify_credentials()
                tw_username = None
                if tw_valid:
                    tw_username = tw_poster.get_username()
                
                result['twitter'] = {
                    'credentials_valid': tw_valid,
                    'username': tw_username
                }
            except Exception as e:
                print(f"❌ Twitter status check failed: {e}")
                result['twitter'] = {
                    'credentials_valid': False,
                    'error': str(e)
                }
        
        if platform == 'instagram' or not platform:
            print("🔍 Status check requested for Instagram")
            try:
                ig_poster = InstagramPoster()
                ig_token_ok = False
                ig_account_ok = False
                ig_username = None
                ig_account_name = None
                
                ig_token_ok = ig_poster and ig_poster.access_token is not None
                if ig_token_ok:
                    account_info = ig_poster.get_account_info()
                    if account_info:
                        ig_account_ok = True
                        ig_username = account_info.get('username')
                        ig_account_name = account_info.get('name')
                
                result['instagram'] = {
                    'token_valid': ig_token_ok,
                    'account_id': getattr(ig_poster, 'ig_id', None),
                    'account_access': ig_account_ok,
                    'username': ig_username,
                    'account_name': ig_account_name
                }
            except Exception as e:
                print(f"❌ Instagram status check failed: {e}")
                result['instagram'] = {
                    'token_valid': False,
                    'account_access': False,
                    'error': str(e)
                }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Simple health check"""
    return jsonify({'status': 'healthy', 'service': 'SocMed Poster'})

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found! Create one with your SocMed credentials.")
        exit(1)
    
    print("🚀 Starting SocMed Poster Web UI...")
    print("📱 Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
