import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LinkedInPoster:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.person_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.api_url = "https://api.linkedin.com/v2"
        
        if not self.access_token or not self.person_id:
            raise ValueError("LinkedIn credentials not found in environment variables")
    
    def verify_credentials(self):
        """Verify LinkedIn API credentials"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/people/{self.person_id}", headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"LinkedIn verification error: {e}")
            return False
    
    def post(self, message):
        """Post text content to LinkedIn"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        post_data = {
            "author": f"urn:li:person:{self.person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(f"{self.api_url}/ugcPosts", json=post_data, headers=headers)
            if response.status_code == 201:
                print("✅ Posted to LinkedIn successfully")
                return True
            else:
                print(f"❌ LinkedIn post failed: {response.text}")
                return False
        except Exception as e:
            print(f"LinkedIn posting error: {e}")
            return False