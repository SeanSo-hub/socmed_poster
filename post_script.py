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
        message = poster.post("Another test post! with improvements")
        
        print("✅ Complete!" if message else "❌ Failed!")
        
    except ValueError as e:
        print(f"❌ Config error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
