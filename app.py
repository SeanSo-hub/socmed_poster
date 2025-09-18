from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
from scripts.fb_script import FacebookPoster
from scripts.twitter_script import TwitterPoster
from scripts.instagram_script import InstagramPoster
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
    # Read the selected platform from query params so the UI can preserve state
    selected_platform = request.args.get('platform', 'facebook')
    return render_template('index.html', selected_platform=selected_platform)

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
                return redirect(url_for('index', platform='facebook'))
            
            poster.get_page_token()
            
            # Handle multiple file uploads for Facebook
            uploaded_files = request.files.getlist('media_file')
            image_files = []
            video_files = []
            temp_files = []  # Keep track for cleanup
            
            # Process uploaded files
            for file in uploaded_files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    temp_files.append(filepath)
                    
                    if file.content_type.startswith('image/') and allowed_file(file.filename, 'image'):
                        image_files.append(filepath)
                    elif file.content_type.startswith('video/') and allowed_file(file.filename, 'video'):
                        video_files.append(filepath)
                    else:
                        # Clean up and return error
                        for temp_file in temp_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        flash('Invalid file type for Facebook. Please upload image or video files only.', 'error')
                        return redirect(url_for('index', platform='facebook'))
            
            # Determine posting method based on uploaded files
            try:
                if len(image_files) > 1:
                    # Multiple images - use multi-photo post
                    if len(image_files) > 10:
                        flash('Facebook allows maximum 10 images per post.', 'error')
                        success = False
                    else:
                        print(f"📸 Posting {len(image_files)} images to Facebook")
                        success = poster.post_multiple_photos(image_files, message if message else None)
                
                elif len(image_files) == 1:
                    # Single image
                    print("📸 Posting single image to Facebook")
                    success = poster.post_photo(image_files[0], message if message else None)
                
                elif len(video_files) == 1:
                    # Single video (Facebook doesn't support multiple videos in one post)
                    print("🎥 Posting video to Facebook")
                    success = poster.post_video(video_files[0], message if message else None)
                
                elif len(video_files) > 1:
                    # Multiple videos not supported
                        flash('Facebook does not support multiple videos in one post. Please upload one video at a time.', 'error')
                        success = False
                
                elif image_files and video_files:
                    # Mixed media not supported
                        flash('Facebook does not support mixing images and videos in one post. Please upload either images or videos, not both.', 'error')
                        success = False
                
                else:
                    # No files uploaded, post text message
                    if not message:
                        flash('Please enter a message or upload files!', 'error')
                        success = False
                    else:
                        print("💬 Posting text message to Facebook")
                        success = poster.post(message, link if link else None)
                
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                        print(f"🗑️ Cleaned up temp file: {temp_file}")
                    except:
                        pass
        
        elif platform == 'twitter':
            # Twitter posting logic
            poster = TwitterPoster()
            
            # Handle multiple file uploads for Twitter (max 4 files)
            uploaded_files = request.files.getlist('media_file')
            media_files = []
            temp_files = []  # Keep track for cleanup
            
            # Process uploaded files
            for file in uploaded_files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    temp_files.append(filepath)
                    
                    if (file.content_type.startswith('image/') and allowed_file(file.filename, 'image')) or \
                       (file.content_type.startswith('video/') and allowed_file(file.filename, 'video')):
                        media_files.append(filepath)
                    else:
                        # Clean up and return error
                        for temp_file in temp_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        flash('Invalid file type for Twitter. Please upload image or video files only.', 'error')
                        return redirect(url_for('index', platform='twitter'))
            
            try:
                # Check Twitter's 4-file limit
                if len(media_files) > 4:
                    flash('Twitter allows maximum 4 media files per tweet.', 'error')
                    success = False
                elif len(media_files) > 0:
                    # Post with media files
                    print(f"📎 Posting {len(media_files)} media file(s) to Twitter")
                    success = poster.post(message if message else "📎 Media post", media_files)
                else:
                    # No files uploaded, post text message
                    if not message:
                        flash('Please enter a message or upload media files!', 'error')
                        success = False
                    else:
                        print("💬 Posting text message to Twitter")
                        success = poster.post(message)
                        
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                        print(f"🗑️ Cleaned up temp file: {temp_file}")
                    except:
                        pass
        
        elif platform == 'instagram':
            try:
                ig = InstagramPoster()
                print(f"✅ Instagram poster initialized for IG ID {ig.ig_id}")

                # Accept multiple images (carousel) OR a single video, not both
                uploaded_files = request.files.getlist('media_file')
                image_files = []
                video_files = []
                temp_files = []

                for file in uploaded_files:
                    if file and file.filename != '':
                        filename = secure_filename(file.filename)
                        temp_dir = os.path.join(UPLOAD_FOLDER, 'temp')
                        os.makedirs(temp_dir, exist_ok=True)
                        filepath = os.path.join(temp_dir, filename)
                        file.save(filepath)
                        temp_files.append(filepath)

                        if file.content_type.startswith('image/') and allowed_file(file.filename, 'image'):
                            image_files.append(filepath)
                        elif file.content_type.startswith('video/') and allowed_file(file.filename, 'video'):
                            video_files.append(filepath)
                        else:
                            for tf in temp_files:
                                try:
                                    os.remove(tf)
                                except:
                                    pass
                            flash('Invalid file type for Instagram. Please upload image or video files only.', 'error')
                            return redirect(url_for('index', platform='instagram'))

                try:
                    # Mixed media not allowed
                    if image_files and video_files:
                        flash('Instagram does not support mixing images and videos in one post. Upload either images (carousel) or a single video.', 'error')
                        success = False

                    # Video posting (only one video allowed per post here)
                    elif len(video_files) == 1:
                        print(f"🎥 Posting single video to Instagram: {video_files[0]}")
                        result = ig.post_video(video_files[0], message if message else '')
                        success = bool(result)
                    elif len(video_files) > 1:
                        flash('Instagram supports one video per post. Please upload a single video.', 'error')
                        success = False

                    # Carousel or single image
                    elif len(image_files) > 1:
                        if len(image_files) > 10:
                            flash('Instagram allows maximum 10 images per carousel post.', 'error')
                            success = False
                        else:
                            print(f"📸 Creating Instagram carousel with {len(image_files)} images")
                            result = ig.post_carousel(image_files, message if message else '')
                            success = bool(result)
                    elif len(image_files) == 1:
                        print("📸 Posting single image to Instagram")
                        result = ig.post_image(image_files[0], message if message else '')
                        success = bool(result)
                    else:
                        # No files uploaded, check link
                        if link and link.startswith('http'):
                            # Accept video URL or image URL
                            if any(ext in link.lower() for ext in ('.mp4', '.mov', '.webm')):
                                print("🔗 Posting video from URL to Instagram")
                                result = ig.post_video(link, message if message else '')
                                success = bool(result)
                            else:
                                print("🔗 Posting image from URL to Instagram")
                                result = ig.post_image(link, message if message else '')
                                success = bool(result)
                        else:
                            flash('Please upload image/video files or provide a publicly accessible media URL for Instagram posts.', 'error')
                            success = False

                finally:
                    for tf in temp_files:
                        try:
                            os.remove(tf)
                            print(f"🗑️ Cleaned up temp file: {tf}")
                        except:
                            pass
            except ValueError as e:
                flash(f'Configuration error: {e}', 'error')
                return redirect(url_for('index', platform='instagram'))
            except Exception as e:
                print(f"Instagram error: {e}")
                flash('Failed to post to Instagram. Check console for details.', 'error')
                return redirect(url_for('index', platform='instagram'))

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
        selected = locals().get('platform', 'facebook')
        return redirect(url_for('index', platform=selected))
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
        selected = locals().get('platform', 'facebook')
        return redirect(url_for('index', platform=selected))


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
                    try:
                        me = tw_poster.client.get_me()
                        if getattr(me, 'data', None):
                            tw_username = getattr(me.data, 'username', None) or me.data.get('username') if isinstance(me.data, dict) else None
                    except Exception as ex:
                        print(f"ℹ️ Could not fetch Twitter username via client.get_me(): {ex}")

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
