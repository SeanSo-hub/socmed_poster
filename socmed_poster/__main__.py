"""Allow running the web app with `python -m socmed_poster`"""
from .web import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting SocMed Poster Web UI (module run)")
    app.run(debug=True, host='0.0.0.0', port=5000)
