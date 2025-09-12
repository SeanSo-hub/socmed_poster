import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class FacebookPoster:
    """Simple Facebook page posting client"""
    
    def __init__(self):
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com"
        
        if not self.page_id or not self.access_token:
            raise ValueError("Missing FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN in .env")
    
    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Facebook API"""
        url = f"{self.base_url}/{endpoint}"
        
        if method == "GET":
            params = {"access_token": self.access_token}
            response = requests.get(url, params=params, timeout=30)
        else:
            payload = {**(data or {}), "access_token": self.access_token}
            response = requests.post(url, data=payload, timeout=30)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            error = response.json().get("error", {}) if response.content else {}
            print(f"❌ Error {error.get('code', '')}: {error.get('message', 'Request failed')}")
            return None
    
    def verify_token(self) -> bool:
        """Verify access token validity"""
        result = self._request("me")
        if result:
            print(f"✅ Token verified: {result.get('name')}")
            return True
        return False
    
    def verify_page_access(self) -> bool:
        """Verify page access"""
        result = self._request(self.page_id)
        if result:
            print(f"✅ Page verified: {result.get('name')}")
            return True
        return False
    
    def get_page_token(self) -> bool:
        """Get and set page access token if available"""
        # First check if we're already using a page token
        me_result = self._request("me")
        if me_result and me_result.get("id") == self.page_id:
            print("🔑 Already using page access token")
            return True
        
        # If not, try to get page token from user token
        result = self._request("me/accounts")
        if result:
            for page in result.get("data", []):
                if str(page.get("id")) == self.page_id:
                    self.access_token = page.get("access_token")
                    print("🔑 Switched to page access token")
                    return True
        print("⚠️ Using page token from user token")
        return False
    
    def post(self, message: str, link: Optional[str] = None) -> bool:
        """Post message to Facebook page"""
        if not message.strip():
            print("❌ Message cannot be empty")
            return False
        
        data = {"message": message}
        if link:
            data["link"] = link
        
        result = self._request(f"{self.page_id}/feed", "POST", data)
        if result:
            print(f"✅ Posted! ID: {result.get('id')}")
            return True
        return False
    
    def post_photo(self, image_path: str, caption: Optional[str] = None) -> bool:
        """Upload and post a photo to Facebook page"""
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
        
        url = f"{self.base_url}/{self.page_id}/photos"
        
        try:
            with open(image_path, "rb") as image_file:
                files = {"source": image_file}
                data = {"access_token": self.access_token}
                if caption:
                    data["caption"] = caption
                
                response = requests.post(url, files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Photo posted! ID: {result.get('id')}")
                    return True
                else:
                    error = response.json().get("error", {}) if response.content else {}
                    print(f"❌ Photo upload failed - Error {error.get('code', '')}: {error.get('message', 'Request failed')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Photo upload error: {e}")
            return False
    
    def post_video(self, video_path: str, description: Optional[str] = None) -> bool:
        """Upload and post a video to Facebook page"""
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        url = f"{self.base_url}/{self.page_id}/videos"
        
        try:
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                data = {"access_token": self.access_token}
                if description:
                    data["description"] = description
                
                response = requests.post(url, files=files, data=data, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Video posted! ID: {result.get('id')}")
                    return True
                else:
                    error = response.json().get("error", {}) if response.content else {}
                    print(f"❌ Video upload failed - Error {error.get('code', '')}: {error.get('message', 'Request failed')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Video upload error: {e}")
            return False

def main():
    """Main execution function"""
    try:
        poster = FacebookPoster()
        
        print("🚀 Initializing Facebook poster...")
        
        # Verify credentials
        if not poster.verify_token() or not poster.verify_page_access():
            print("❌ Authentication failed")
            return
        
        # Try to get page token for better permissions
        poster.get_page_token()
        
        # Post message
        message = poster.post("Test for standalone script!")
        
        # Uncomment to test photo upload:
        # photo_success = poster.post_photo("./test_image.jpg", "Test photo from standalone script!")
        
        # Uncomment to test video upload:
        # video_success = poster.post_video("./test_video.mp4", "Test video from standalone script!")
        
        print("✅ Complete!" if message else "❌ Failed!")
        
    except ValueError as e:
        print(f"❌ Config error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
