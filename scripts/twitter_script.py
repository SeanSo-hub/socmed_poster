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
        if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
            raise ValueError("Missing Twitter API credentials in .env file")
        
        # API v2 client (tweets)
        self.client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True  # ✅ auto-wait for v2 rate limits
        )
        
        # API v1.1 client (media upload)
        auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)  # ✅ auto-wait for v1.1
    
    def verify_credentials(self) -> bool:
        """Check if credentials work (only call when needed)"""
        print("🔍 Verifying Twitter credentials...")
        try:
            me = self.client.get_me()
            if me and getattr(me, "data", None):
                print(f"✅ Verified: @{me.data.username}")
                return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
        return False

    def _retry_operation(self, operation, *args, max_retries=3, operation_name="operation"):
        """Retry wrapper with rate-limit handling"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 {operation_name} (retry {attempt + 1}/{max_retries})")
                return operation(*args)

            except tweepy.TooManyRequests as e:
                reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + 900))
                wait_for = max(0, reset_time - int(time.time()))
                print(f"⚠️ Rate limit hit. Waiting {wait_for} seconds...")
                time.sleep(wait_for)
                continue

            except (requests.exceptions.ConnectionError,
                    ConnectionResetError,
                    requests.exceptions.Timeout) as e:
                last_error = e
                wait_time = (attempt + 1) * 3
                print(f"🌐 Connection error: {e}, retrying in {wait_time}s...")
                time.sleep(wait_time)

            except Exception as e:
                last_error = e
                wait_time = (attempt + 1) * 2
                print(f"❌ {operation_name} error: {e}, retrying in {wait_time}s...")
                time.sleep(wait_time)

        print(f"❌ {operation_name} failed after {max_retries} retries")
        if last_error:
            print(f"💥 Final error: {last_error}")
        return None
    
    def upload_media(self, file_path: str) -> Optional[str]:
        """Upload image/video to Twitter"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        # Determine media type and use chunked upload for large files/videos
        def _upload():
            try:
                ext = os.path.splitext(file_path)[1].lower()
                is_video = ext in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

                if is_video:
                    # Use chunked upload for videos with media_category set to 'tweet_video'
                    media = self.api.media_upload(filename=file_path, chunked=True, media_category='tweet_video')
                else:
                    # images and small media can use the simple upload
                    media = self.api.media_upload(filename=file_path)

                media_id = getattr(media, 'media_id', None) or getattr(media, 'media_id_string', None)
                if media_id:
                    print(f"✅ Uploaded media: {media_id} ({'video' if is_video else 'image'})")
                    return str(media_id)
                print(f"❌ Upload returned no media id for {file_path}")
                return None

            except Exception as e:
                print(f"❌ Media upload failed for {file_path}: {e}")
                raise

        return self._retry_operation(_upload, operation_name="Media upload")

    def post(self, message: str, media_files: Optional[List[str]] = None) -> bool:
        """Post a tweet"""
        if not message.strip() and not media_files:
            print("❌ Empty tweet not allowed")
            return False
        if len(message) > 280:
            print(f"❌ Too long: {len(message)} chars (max 280)")
            return False

        media_ids = []
        if media_files:
            if len(media_files) > 4:
                print("⚠️ Max 4 media per tweet, truncating list")
                media_files = media_files[:4]

            # Upload each media file; abort if any upload fails
            for f in media_files:
                media_id = self.upload_media(f)
                if not media_id:
                    print(f"❌ Aborting tweet: failed to upload media {f}")
                    return False
                media_ids.append(media_id)

        def _post():
            if media_ids:
                # Try v2 client first: many tweepy versions accept media_ids kwarg
                try:
                    response = self.client.create_tweet(text=message, media_ids=media_ids)
                    print(f"✅ Tweet posted with {len(media_ids)} media file(s) (v2 client)")

                    if getattr(response, 'data', None):
                        tweet_id = response.data.get('id') if isinstance(response.data, dict) else getattr(response.data, 'id', None)
                        if tweet_id:
                            print(f"🔗 https://twitter.com/user/status/{tweet_id}")
                    return True

                except TypeError as te:
                    # Older tweepy may not accept media_ids on Client.create_tweet; fall back to v1.1 API
                    print(f"ℹ️ v2 client create_tweet media_ids unsupported: {te}. Falling back to v1.1 API.")

                except Exception as e:
                    # Let retry wrapper handle other transient errors
                    print(f"❌ Tweet posting error (v2 client): {e}")
                    raise

                # Fallback: use v1.1 API.update_status with media_ids (media_ids must be list of ints)
                try:
                    numeric_media_ids = [int(m) for m in media_ids]
                    status = self.api.update_status(status=message, media_ids=numeric_media_ids)
                    # update_status returns a Status object with id
                    sid = getattr(status, 'id', None)
                    if sid:
                        print(f"✅ Tweet posted with {len(media_ids)} media file(s) (v1.1 API)")
                        print(f"🔗 https://twitter.com/user/status/{sid}")
                        return True
                    return False
                except Exception as e:
                    print(f"❌ Tweet posting error (v1.1 fallback): {e}")
                    raise

            else:
                # No media, simple v2 client post
                response = self.client.create_tweet(text=message)
                print("✅ Tweet posted")
                return True

        return self._retry_operation(_post, operation_name="Tweet posting") is not None


# Convenience wrappers
def post_tweet(message: str, media_files: Optional[List[str]] = None) -> bool:
    try:
        poster = TwitterPoster()
        # ⚠️ Skip verify_credentials unless explicitly needed
        return poster.post(message, media_files)
    except Exception as e:
        print(f"❌ Failed to init TwitterPoster: {e}")
        return False

def post_with_image(message: str, image_path: str) -> bool:
    return post_tweet(message, [image_path])

def post_with_video(message: str, video_path: str) -> bool:
    return post_tweet(message, [video_path])


if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    if post_tweet(f"Test post at {timestamp} ⏱"):
        print("🎉 Success!")
    else:
        print("💥 Failed.")
