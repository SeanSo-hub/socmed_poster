import os
from flask import Blueprint, send_from_directory, current_app
from werkzeug.utils import secure_filename

utils_bp = Blueprint('utils', __name__)

@utils_bp.route('/public_uploads/<path:filename>')
def public_upload(filename):
    upload_folder = current_app.config.get('UPLOAD_PUBLIC_FOLDER')
    return send_from_directory(upload_folder, filename)


# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', '3gp'}


def allowed_file(filename, file_type=None):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): The filename to check
        file_type (str): Optional file type filter ('image' or 'video')
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return extension in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return extension in ALLOWED_VIDEO_EXTENSIONS
    else:
        # Allow both image and video if no specific type is requested
        return extension in ALLOWED_IMAGE_EXTENSIONS or extension in ALLOWED_VIDEO_EXTENSIONS


def get_file_type(filename):
    """
    Determine if a file is an image or video based on its extension.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        str: 'image', 'video', or 'unknown'
    """
    if not filename or '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif extension in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    else:
        return 'unknown'


def create_upload_folder(upload_path):
    """
    Create upload folder if it doesn't exist.
    
    Args:
        upload_path (str): Path to the upload folder
    """
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)


def clean_filename(filename):
    """
    Clean and secure a filename.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: A cleaned, secure filename
    """
    return secure_filename(filename)
