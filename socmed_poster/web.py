import os
from flask import Flask


def create_app():
    """Create and configure the Flask application (same behavior as original app.py)."""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = os.urandom(24)

    upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['UPLOAD_PUBLIC_FOLDER'] = os.path.join(upload_folder, 'public')
    app.config['ALLOWED_EXTENSIONS'] = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    }
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_PUBLIC_FOLDER'], exist_ok=True)

    # Register blueprints (import from package routes)
    from .routes import main_bp, api_bp, utils_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(utils_bp)

    return app
