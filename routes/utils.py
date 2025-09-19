import os
from flask import Blueprint, send_from_directory, current_app

utils_bp = Blueprint('utils', __name__)


@utils_bp.route('/public_uploads/<path:filename>')
def public_upload(filename):
    """Serve files placed in the uploads/public directory."""
    upload_folder = current_app.config.get('UPLOAD_PUBLIC_FOLDER')
    return send_from_directory(upload_folder, filename)


def allowed_file(filename, file_type):
    """Check file extension against current app config."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {})
    return ext in allowed.get(file_type, set())
