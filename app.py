from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from post_script import FacebookPoster
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

@app.route('/')
def index():
    """Main page with posting form"""
    return render_template('index.html')

@app.route('/post', methods=['POST'])
def post_message():
    """Handle message posting"""
    try:
        message = request.form.get('message', '').strip()
        link = request.form.get('link', '').strip()
        
        if not message:
            flash('Message cannot be empty!', 'error')
            return redirect(url_for('index'))
        
        # Create poster and attempt to post
        poster = FacebookPoster()
        
        # Verify credentials
        if not poster.verify_token() or not poster.verify_page_access():
            flash('Authentication failed. Check your credentials.', 'error')
            return redirect(url_for('index'))
        
        # Try to get page token
        poster.get_page_token()
        
        # Post the message
        success = poster.post(message, link if link else None)
        
        if success:
            flash(f'Message posted successfully!', 'success')
        else:
            flash('Failed to post message. Check console for details.', 'error')
            
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
