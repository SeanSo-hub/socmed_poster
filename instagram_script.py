import os
import requests
import json
import time
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Load .env from repository root if present
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    # fallback to default load (will still load if environment variables are set)
    load_dotenv()

class InstagramPoster:
    """Instagram direct posting via Graph API (Business/Creator Account)"""

    def __init__(self):
        self.ig_id = os.getenv("INSTAGRAM_USER_ID")       # Instagram Business User ID
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")  # IG Access Token
        self.base_url = "https://graph.facebook.com/v23.0"

        if not self.ig_id or not self.access_token:
            raise ValueError("Missing INSTAGRAM_USER_ID or INSTAGRAM_ACCESS_TOKEN in .env")

    def get_account_info(self) -> Optional[dict]:
        """Get Instagram account information including username"""
        print("🔍 Checking Instagram connection...")
        try:
            url = f"{self.base_url}/{self.ig_id}"
            # account_type is not valid on IGUser for some Graph API versions; request only username and name
            params = {
                'fields': 'username,name',
                'access_token': self.access_token
            }

            # Retry once on transient network errors
            for attempt in range(2):
                try:
                    response = requests.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        if result:
                            print(f"✅ Instagram connection verified for: @{result.get('username', 'unknown')}")
                        return result
                    elif response.status_code == 400:
                        # Likely requested an invalid field or bad params
                        print(f"❌ Failed to get Instagram account info (400): {response.text}")
                        break
                    else:
                        print(f"❌ Failed to get Instagram account info: {response.status_code} {response.text}")
                        break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    print(f"🌐 Transient network error getting Instagram account info (attempt {attempt+1}): {e}")
                    time.sleep(2 * (attempt + 1))
                    continue
        except Exception as e:
            print(f"❌ Error getting Instagram account info: {e}")
        return None

    def post_image(self, image_url: str, caption: str):
        """Publish an image post"""
        # If a local file path is provided, and Cloudinary credentials are available,
        # upload the file to Cloudinary and use the returned secure URL.
        if not image_url.startswith('http'):
            # treat image_url as a local file path
            uploaded = self._upload_to_cloudinary(image_url)
            if not uploaded:
                print("❌ Could not upload local file to Cloudinary. Provide a public URL or set Cloudinary env vars.")
                return None
            image_url = uploaded

        # Step 1: Create media container
        container_url = f"{self.base_url}/{self.ig_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(container_url, data=payload)
        data = res.json()

        if "id" not in data:
            print("❌ Failed to create media container:", data)
            return None

        # helper moved to class scope

        container_id = data["id"]
        print(f"📦 Created media container: {container_id}")

        # Step 2: Publish the container
        publish_url = f"{self.base_url}/{self.ig_id}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        res = requests.post(publish_url, data=payload)
        result = res.json()

        if "id" in result:
            print(f"✅ Successfully posted! IG Post ID: {result['id']}")
            return result["id"]
        else:
            print("❌ Failed to publish:", result)
            return None

    def _upload_to_imgur(self, file_path: str) -> Optional[str]:
        """Upload a local image to Imgur anonymously and return the public URL.

        Requires `IMGUR_CLIENT_ID` in environment.
        """
        client_id = os.getenv('IMGUR_CLIENT_ID')
        if not client_id:
            print("⚠️ IMGUR_CLIENT_ID not set in environment. Cannot auto-upload local file.")
            return None

        upload_url = 'https://api.imgur.com/3/image'
        try:
            with open(file_path, 'rb') as f:
                files = {'image': f}
                headers = {'Authorization': f'Client-ID {client_id}'}
                resp = requests.post(upload_url, headers=headers, files=files, timeout=30)
            result = resp.json()
        except Exception as e:
            print(f"❌ Error uploading to Imgur: {e}")
            return None

        if not result.get('success'):
            print(f"❌ Imgur upload failed: {result}")
            return None

        link = result.get('data', {}).get('link')
        print(f"✅ Uploaded to Imgur: {link}")
        return link

    def _upload_to_cloudinary(self, file_path: str) -> Optional[str]:
        """Upload a local file to Cloudinary and return the secure URL.

        Supports two modes:
        1. Signed uploads: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
        2. Unsigned uploads: CLOUDINARY_CLOUD_NAME and CLOUDINARY_UPLOAD_PRESET
        """
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        upload_preset = os.getenv('CLOUDINARY_UPLOAD_PRESET')
        
        def _mask(s: Optional[str]) -> str:
            if not s:
                return '(empty)'
            s = s.strip()
            if len(s) <= 6:
                return s
            return f"{s[:3]}...{s[-3:]}"

        if not cloud_name:
            print('⚠️ Cloudinary not configured - CLOUDINARY_CLOUD_NAME missing.')
            return None

        # Check which mode to use - prefer unsigned (preset) for easier setup
        use_unsigned = upload_preset
        use_signed = api_key and api_secret and not upload_preset
        
        if not use_unsigned and not use_signed:
            print('⚠️ Cloudinary not configured properly.')
            print(f"For unsigned uploads (recommended): set CLOUDINARY_UPLOAD_PRESET={_mask(upload_preset)}")
            print(f"For signed uploads: set CLOUDINARY_API_KEY={_mask(api_key)} and CLOUDINARY_API_SECRET={_mask(api_secret)}")
            return None

        url = f'https://api.cloudinary.com/v1_1/{cloud_name}/image/upload'
        if not os.path.exists(file_path):
            print(f'❌ Local file not found: {file_path}')
            return None

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                
                if use_unsigned:
                    # Unsigned upload with preset (recommended)
                    data = {'upload_preset': upload_preset}
                    print(f"📝 Using unsigned Cloudinary upload with preset {_mask(upload_preset)}")
                else:
                    # Signed upload with API key and secret (fallback)
                    import time
                    import hashlib
                    
                    timestamp = int(time.time())
                    params_to_sign = {
                        'timestamp': timestamp,
                        'folder': 'socmed_poster'
                    }
                    
                    # Create signature according to Cloudinary docs
                    # Sort parameters and create string: param1=value1&param2=value2
                    params_str = '&'.join([f"{k}={v}" for k, v in sorted(params_to_sign.items())])
                    # Append API secret to the end
                    string_to_sign = params_str + api_secret
                    
                    # Generate SHA1 hash
                    signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
                    
                    data = {
                        'api_key': api_key,
                        'timestamp': timestamp,
                        'signature': signature,
                        'folder': 'socmed_poster'
                    }
                    print(f"� Using signed Cloudinary upload (fallback)")
                
                resp = requests.post(url, data=data, files=files, timeout=60)
            
            # Check response status first
            if resp.status_code != 200:
                print(f'❌ Cloudinary upload failed with status {resp.status_code}')
                print(f'Response body: {resp.text[:500]}')
                return None
            
            # Try to parse JSON response
            try:
                result = resp.json()
            except json.JSONDecodeError as json_err:
                print(f'❌ Cloudinary returned invalid JSON: {json_err}')
                print(f'Response body: {resp.text[:500]}')
                return None
                
        except Exception as e:
            print(f'❌ Error uploading to Cloudinary: {e}')
            return None

        if 'secure_url' not in result:
            print(f'❌ Cloudinary upload failed - no secure_url in response: {result}')
            return None

        secure = result.get('secure_url')
        print(f'✅ Uploaded to Cloudinary: {secure}')
        return secure


def main():
    poster = InstagramPoster()

    # Run token diagnostics before attempting to post
    def _mask(t: str) -> str:
        if not t:
            return "(empty)"
        t = t.strip()
        if len(t) <= 12:
            return t
        return f"{t[:6]}...{t[-6:]}"

    print(f"Using INSTAGRAM_USER_ID={poster.ig_id}")
    print(f"Using INSTAGRAM_ACCESS_TOKEN={_mask(poster.access_token)}")

    # Try to debug token using app token if available
    app_token = os.getenv('FACEBOOK_APP_ACCESS_TOKEN')
    debug_access = app_token or poster.access_token
    debug_url = f"https://graph.facebook.com/debug_token"
    params = {"input_token": poster.access_token, "access_token": debug_access}
    try:
        r = requests.get(debug_url, params=params, timeout=10)
        dj = r.json()
        if 'error' in dj:
            print("❌ debug_token response error:", dj['error'])
        else:
            print("🔍 debug_token:", dj.get('data'))
            if not dj.get('data', {}).get('is_valid'):
                print("❌ Token reported as invalid by debug_token endpoint.")
                return
    except Exception as e:
        print("⚠️ Could not call debug_token endpoint:", e)

    # Example: post using a public image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"
    caption = "🚀 Hello Instagram from da free world!"
    poster.post_image(image_url, caption)


if __name__ == "__main__":
    main()
