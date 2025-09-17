import tweepy
import os
import time
import requests
import datetime
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET_TOKEN")

class TwitterPoster:
    """Twitter posting client with media upload support"""
    
    def __init__(self):
        # Validate credentials first
        if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
            raise ValueError("Missing Twitter API credentials in .env file")
        
        # API v2 client for posting tweets
        self.client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        
        # API v1.1 for media uploads
        auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
    
    def verify_credentials(self) -> bool:
        """Verify Twitter API credentials are working"""
        print("🔍 Checking Twitter connection...")
        try:
            me = self.client.get_me()  # Removed invalid timeout parameter
            if me.data:
                print(f"✅ Twitter credentials verified for: @{me.data.username}")
                return True
        except Exception as e:
            print(f"❌ Twitter credential verification failed: {e}")
        return False
    
    def get_username(self) -> Optional[str]:
        """Get the authenticated user's Twitter username.

        Strategy:
        - Try Twitter API v2 `get_me()` with retries for transient errors
        - If that fails, fall back to v1.1 `api.verify_credentials()` to obtain `screen_name`
        - Handle connection resets gracefully and return None if unavailable
        """
        # Try v2 client.get_me() with retry logic (silent failures)
        for attempt in range(3):
            try:
                me = self.client.get_me()
                if me and getattr(me, 'data', None):
                    return me.data.username
                break
            except (requests.exceptions.ConnectionError, ConnectionResetError, requests.exceptions.Timeout):
                time.sleep(2 * (attempt + 1))
                continue
            except Exception:
                break

        # Fallback to v1.1 API (verify_credentials) which returns screen_name (silent)
        try:
            user = self.api.verify_credentials()
            if user and getattr(user, 'screen_name', None):
                return user.screen_name
        except Exception:
            pass

        # Nothing worked
        return None
    
    def _retry_operation(self, operation, *args, max_retries=3, operation_name="operation"):
        """Enhanced retry logic with better error handling"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 {operation_name} (Attempt {attempt + 1}/{max_retries})")
                
                return operation(*args)
                
            except tweepy.TooManyRequests as e:
                print("⚠️ Rate limit reached. Waiting 15 minutes...")
                time.sleep(900)  # Wait 15 minutes
                
            except (requests.exceptions.ConnectionError, 
                   ConnectionResetError, 
                   requests.exceptions.Timeout) as e:
                last_error = e
                print(f"🌐 Connection error: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9 seconds
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
            except tweepy.Forbidden as e:
                print(f"❌ Forbidden (403): {e}")
                print("💡 This might be duplicate content or API access restrictions")
                return None
                
            except tweepy.Unauthorized as e:
                print(f"❌ Unauthorized (401): {e}")
                print("💡 Check your API credentials")
                return None
                
            except tweepy.BadRequest as e:
                print(f"❌ Bad Request (400): {e}")
                print("💡 Check your request parameters")
                return None
                
            except Exception as e:
                last_error = e
                print(f"❌ {operation_name} error: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        print(f"❌ {operation_name} failed after {max_retries} attempts")
        if last_error:
            print(f"💥 Final error: {last_error}")
        return None
    
    def upload_media(self, file_path: str) -> Optional[str]:
        """Upload media file with better error handling"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        print(f"📤 Uploading media: {os.path.basename(file_path)}")
        
        def _upload():
            media = self.api.media_upload(file_path)
            print(f"✅ Media uploaded successfully! ID: {media.media_id}")
            return str(media.media_id)
        
        return self._retry_operation(_upload, operation_name="Media upload")
    
    def post(self, message: str, media_files: Optional[List[str]] = None) -> bool:
        """Post a tweet with enhanced error handling"""
        if not message.strip() and not media_files:
            print("❌ Cannot post empty tweet without media")
            return False
        
        # Twitter character limit check
        if len(message) > 280:
            print(f"❌ Tweet too long: {len(message)} characters (max 280)")
            return False
        
        media_ids = []
        
        # Upload media files if provided
        if media_files:
            if len(media_files) > 4:
                print("⚠️ Twitter allows max 4 media files. Using first 4.")
                media_files = media_files[:4]
            
            for file_path in media_files:
                media_id = self.upload_media(file_path)
                if media_id:
                    media_ids.append(media_id)
                else:
                    print(f"⚠️ Skipping failed upload: {file_path}")
        
        if not message.strip() and not media_ids:
            print("❌ No content to post (message empty and no media uploaded)")
            return False
        
        print(f"📝 Posting tweet: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
        def _post():
            if media_ids:
                response = self.client.create_tweet(text=message, media_ids=media_ids)
                print(f"✅ Tweet with {len(media_ids)} media file(s) posted!")
            else:
                response = self.client.create_tweet(text=message)
                print("✅ Tweet posted successfully!")
            
            if response.data:
                tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
                print(f"🔗 {tweet_url}")
                return True
            return False
        
        result = self._retry_operation(_post, operation_name="Tweet posting")
        return result is not None

# Convenience functions
def post_tweet(message: str, media_files: Optional[List[str]] = None) -> bool:
    """Post a tweet with optional media"""
    try:
        poster = TwitterPoster()
        verified = poster.verify_credentials()
        if not verified:
            print("❌ Twitter credentials verification failed. Aborting post.")
            return False

        # print positive confirmation before attempting uploads/posts
        print("✅ Twitter credentials verified — proceeding to post.")
        return poster.post(message, media_files)
    except Exception as e:
        print(f"❌ Failed to create TwitterPoster: {e}")
        return False

def post_with_image(message: str, image_path: str) -> bool:
    """Post a tweet with a single image"""
    return post_tweet(message, [image_path])

def post_with_video(message: str, video_path: str) -> bool:
    """Post a tweet with a single video"""
    return post_tweet(message, [video_path])

if __name__ == "__main__":
    # Test with a unique message to avoid duplicate content errors
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    success = post_tweet(f"Testing Twitter API at {timestamp} 🔧")
    
    if success:
        print("🎉 Twitter posting is working!")
    else:
        print("💥 Twitter posting failed.")