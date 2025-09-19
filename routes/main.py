import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

from scripts.fb_script import FacebookPoster
from scripts.twitter_script import TwitterPoster
from scripts.instagram_script import InstagramPoster

from .utils import allowed_file

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main page with posting form"""
    selected_platform = request.args.get('platform', 'facebook')
    return render_template('index.html', selected_platform=selected_platform)


@main_bp.route('/post', methods=['POST'])
def post_message():
    """Handle message posting with optional media for Facebook, Twitter, Instagram."""
    try:
        message = request.form.get('message', '').strip()
        platform = request.form.get('platform', 'facebook').strip()
        link = request.form.get('link', '').strip()
        success = False

        upload_folder = current_app.config.get('UPLOAD_FOLDER')

        # Facebook
        if platform == 'facebook':
            poster = FacebookPoster()

            if not poster.verify_token() or not poster.verify_page_access():
                flash('Facebook authentication failed. Check your credentials.', 'error')
                return redirect(url_for('main.index', platform='facebook'))

            poster.get_page_token()

            uploaded_files = request.files.getlist('media_file')
            image_files = []
            video_files = []
            temp_files = []

            for file in uploaded_files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    temp_files.append(filepath)

                    if file.content_type.startswith('image/') and allowed_file(filename, 'image'):
                        image_files.append(filepath)
                    elif file.content_type.startswith('video/') and allowed_file(filename, 'video'):
                        video_files.append(filepath)
                    else:
                        for temp_file in temp_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        flash('Invalid file type for Facebook. Please upload image or video files only.', 'error')
                        return redirect(url_for('main.index', platform='facebook'))

            try:
                if len(image_files) > 1:
                    if len(image_files) > 10:
                        flash('Facebook allows maximum 10 images per post.', 'error')
                        success = False
                    else:
                        print(f"📸 Posting {len(image_files)} images to Facebook")
                        success = poster.post_multiple_photos(image_files, message if message else None)
                elif len(image_files) == 1:
                    print("📸 Posting single image to Facebook")
                    success = poster.post_photo(image_files[0], message if message else None)
                elif len(video_files) == 1:
                    print("🎥 Posting video to Facebook")
                    success = poster.post_video(video_files[0], message if message else None)
                elif len(video_files) > 1:
                    flash('Facebook does not support multiple videos in one post. Please upload one video at a time.', 'error')
                    success = False
                elif image_files and video_files:
                    flash('Facebook does not support mixing images and videos in one post. Please upload either images or videos, not both.', 'error')
                    success = False
                else:
                    if not message:
                        flash('Please enter a message or upload files!', 'error')
                        success = False
                    else:
                        print("💬 Posting text message to Facebook")
                        success = poster.post(message, link if link else None)
            finally:
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                        print(f"🗑️ Cleaned up temp file: {temp_file}")
                    except:
                        pass

        # Twitter
        elif platform == 'twitter':
            poster = TwitterPoster()
            uploaded_files = request.files.getlist('media_file')
            media_files = []
            temp_files = []

            for file in uploaded_files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    temp_files.append(filepath)

                    if (file.content_type.startswith('image/') and allowed_file(filename, 'image')) or \
                       (file.content_type.startswith('video/') and allowed_file(filename, 'video')):
                        media_files.append(filepath)
                    else:
                        for temp_file in temp_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        flash('Invalid file type for Twitter. Please upload image or video files only.', 'error')
                        return redirect(url_for('main.index', platform='twitter'))

            try:
                if len(media_files) > 4:
                    flash('Twitter allows maximum 4 media files per tweet.', 'error')
                    success = False
                elif len(media_files) > 0:
                    print(f"📎 Posting {len(media_files)} media file(s) to Twitter")
                    success = poster.post(message if message else "📎 Media post", media_files)
                else:
                    if not message:
                        flash('Please enter a message or upload media files!', 'error')
                        success = False
                    else:
                        print("💬 Posting text message to Twitter")
                        success = poster.post(message)
            finally:
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                        print(f"🗑️ Cleaned up temp file: {temp_file}")
                    except:
                        pass

        # Instagram
        elif platform == 'instagram':
            try:
                ig = InstagramPoster()
                print(f"✅ Instagram poster initialized for IG ID {ig.ig_id}")

                uploaded_files = request.files.getlist('media_file')
                image_files = []
                video_files = []
                temp_files = []

                for file in uploaded_files:
                    if file and file.filename != '':
                        filename = secure_filename(file.filename)
                        temp_dir = os.path.join(upload_folder, 'temp')
                        os.makedirs(temp_dir, exist_ok=True)
                        filepath = os.path.join(temp_dir, filename)
                        file.save(filepath)
                        temp_files.append(filepath)

                        if file.content_type.startswith('image/') and allowed_file(filename, 'image'):
                            image_files.append(filepath)
                        elif file.content_type.startswith('video/') and allowed_file(filename, 'video'):
                            video_files.append(filepath)
                        else:
                            for tf in temp_files:
                                try:
                                    os.remove(tf)
                                except:
                                    pass
                            flash('Invalid file type for Instagram. Please upload image or video files only.', 'error')
                            return redirect(url_for('main.index', platform='instagram'))

                try:
                    if image_files and video_files:
                        flash('Instagram does not support mixing images and videos in one post. Upload either images (carousel) or a single video.', 'error')
                        success = False
                    elif len(video_files) == 1:
                        print(f"🎥 Posting single video to Instagram: {video_files[0]}")
                        result = ig.post_video(video_files[0], message if message else '')
                        success = bool(result)
                    elif len(video_files) > 1:
                        flash('Instagram supports one video per post. Please upload a single video.', 'error')
                        success = False
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
                        if link and link.startswith('http'):
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
                return redirect(url_for('main.index', platform='instagram'))
            except Exception as e:
                print(f"Instagram error: {e}")
                flash('Failed to post to Instagram. Check console for details.', 'error')
                return redirect(url_for('main.index', platform='instagram'))

        else:
            flash('Invalid platform selected.', 'error')
            return redirect(url_for('main.index'))

        if success:
            platform_name = 'Facebook' if platform == 'facebook' else 'Twitter' if platform == 'twitter' else 'Instagram' if platform == 'instagram' else platform.title()
            flash(f'Content posted successfully to {platform_name}!', 'success')
        else:
            flash(f'Failed to post content to {platform}. Check console for details.', 'error')

        return redirect(url_for('main.index', platform=platform))

    except ValueError as e:
        flash(f'Configuration error: {e}', 'error')
        selected = locals().get('platform', 'facebook')
        return redirect(url_for('main.index', platform=selected))
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
        selected = locals().get('platform', 'facebook')
        return redirect(url_for('main.index', platform=selected))
