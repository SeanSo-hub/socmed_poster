import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LinkedInPoster:
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.person_id = os.getenv('LINKEDIN_PERSON_ID')
        self.api_url = "https://api.linkedin.com/v2"
        
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not found in environment variables")
        
        # If person_id is not provided, try to get it automatically
        if not self.person_id:
            print("⚠️  LINKEDIN_PERSON_ID not found, attempting to retrieve automatically...")
            self.person_id = self._fetch_person_id()
            if not self.person_id:
                raise ValueError("Could not retrieve LinkedIn Person ID. Please set LINKEDIN_PERSON_ID in environment variables")
    
    def _fetch_person_id(self):
        """Internal method to fetch person ID"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                person_id = user_data.get('id')
                print(f"✅ Auto-retrieved Person ID: {person_id}")
                return person_id
            else:
                print(f"❌ Failed to auto-retrieve person ID: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error auto-retrieving person ID: {e}")
            return None
    
    def verify_credentials(self):
        """Verify LinkedIn API credentials"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Use the correct endpoint to get current user info
            response = requests.get(f"{self.api_url}/me", headers=headers)
            if response.status_code == 200:
                print(f"✅ LinkedIn credentials verified for user: {response.json().get('localizedFirstName', 'Unknown')}")
                return True
            else:
                print(f"❌ LinkedIn credential verification failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"LinkedIn verification error: {e}")
            return False
    
    def get_person_id(self):
        """Get the current user's person ID"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.api_url}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                person_id = user_data.get('id')
                print(f"✅ Person ID: {person_id}")
                return person_id
            else:
                print(f"❌ Failed to get person ID: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting person ID: {e}")
            return None
    
    def post(self, message):
        """Post text content to LinkedIn"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Updated API structure for LinkedIn API v2
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
                print(f"❌ LinkedIn post failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"LinkedIn posting error: {e}")
            return False