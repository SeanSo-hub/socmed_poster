from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Configure upload settings
    upload_folder = os.path.abspath('uploads')
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['UPLOAD_PUBLIC_FOLDER'] = os.path.join(upload_folder, 'public')
    app.config['ALLOWED_EXTENSIONS'] = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
    }
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_PUBLIC_FOLDER'], exist_ok=True)

    # Register blueprints
    from routes import main_bp, api_bp, utils_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(utils_bp)

    return app


if __name__ == '__main__':
    # Check for .env
    if not os.path.exists('.env'):
        print("❌ .env file not found! Create one with your SocMed credentials.")
        exit(1)

    app = create_app()
    print("🚀 Starting SocMed Poster Web UI...")
    print("📱 Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
