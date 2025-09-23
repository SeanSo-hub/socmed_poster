import dataclasses
import logging
import os
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Settings:
    facebook_page_id: Optional[str] = os.getenv("FACEBOOK_PAGE_ID")
    facebook_access_token: Optional[str] = os.getenv("FACEBOOK_ACCESS_TOKEN")
    base_url: str = "https://graph.facebook.com"
    request_timeout: int = 30


def _build_session(timeout: int = 30) -> requests.Session:
    """Create a requests.Session with retries configured."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS", "POST"),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    # store a default timeout on session for convenience (not enforced by requests)
    session.request_timeout = timeout  # type: ignore[attr-defined]
    return session


class FacebookPoster:
    """Simple Facebook page posting client with safe defaults and structured logging."""

    def __init__(self, settings: Optional[Settings] = None, session: Optional[requests.Session] = None) -> None:
        self.settings = settings or Settings()
        self.page_id = self.settings.facebook_page_id
        self.access_token = self.settings.facebook_access_token
        self.base_url = self.settings.base_url
        self.timeout = self.settings.request_timeout

        if not self.page_id or not self.access_token:
            raise ValueError("Missing FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN in environment")

        self.session = session or _build_session(timeout=self.timeout)

    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Facebook API using the shared session."""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                params = {"access_token": self.access_token}
                resp = self.session.get(url, params=params, timeout=self.timeout)
            else:
                payload = {**(data or {}), "access_token": self.access_token}
                resp = self.session.post(url, data=payload, timeout=self.timeout)

            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as exc:
            # Try to extract helpful error body
            error = {}
            try:
                error = resp.json().get("error", {}) if resp is not None and resp.content else {}
            except Exception:
                pass

            error_code = error.get("code", "")
            error_message = error.get("message", str(exc))

            if error_code == 190:
                logger.error("Facebook token expired: %s", error_message)
                logger.info("Please refresh your Facebook access token in your environment variables")
            else:
                logger.error("Facebook API Error %s: %s", error_code, error_message)

            return None

    def verify_token(self) -> bool:
        """Verify access token validity"""
        logger.debug("Checking Facebook connection for page_id=%s", self.page_id)
        result = self._request("me")
        if result:
            logger.info("Token verified: %s", result.get("name"))
            return True
        logger.warning("Token verification failed")
        return False

    def verify_page_access(self) -> bool:
        """Verify page access"""
        logger.debug("Checking access to Facebook page %s", self.page_id)
        result = self._request(self.page_id)
        if result:
            logger.info("Page verified: %s", result.get("name"))
            return True
        logger.warning("Page verification failed for %s", self.page_id)
        return False

    def get_page_token(self) -> bool:
        """Get and set page access token if available"""
        me_result = self._request("me")
        if me_result and me_result.get("id") == self.page_id:
            logger.debug("Already using page access token")
            return True

        result = self._request("me/accounts")
        if result:
            for page in result.get("data", []):
                if str(page.get("id")) == self.page_id:
                    self.access_token = page.get("access_token")
                    logger.info("Switched to page access token")
                    return True

        logger.warning("Using page token from user token (no page token found)")
        return False

    def post(self, message: str, link: Optional[str] = None) -> bool:
        """Post message to Facebook page"""
        if not message.strip():
            logger.error("Message cannot be empty")
            return False

        data: Dict[str, Any] = {"message": message}
        if link:
            data["link"] = link

        result = self._request(f"{self.page_id}/feed", "POST", data)
        if result:
            logger.info("Posted! ID: %s", result.get("id"))
            return True
        logger.error("Failed to create post")
        return False

    def post_photo(self, image_path: str, caption: Optional[str] = None) -> bool:
        """Upload and post a photo to Facebook page"""
        if not os.path.exists(image_path):
            logger.error("Image file not found: %s", image_path)
            return False

        url = f"{self.base_url}/{self.page_id}/photos"

        try:
            with open(image_path, "rb") as image_file:
                files = {"source": image_file}
                data = {"access_token": self.access_token}
                if caption:
                    data["caption"] = caption

                resp = self.session.post(url, files=files, data=data, timeout=60)

                if resp.status_code == 200:
                    result = resp.json()
                    logger.info("Photo posted! ID: %s", result.get("id"))
                    return True
                else:
                    error = resp.json().get("error", {}) if resp.content else {}
                    logger.error("Photo upload failed - Error %s: %s", error.get("code", ""), error.get("message", "Request failed"))
                    return False

        except Exception as exc:
            logger.exception("Photo upload error: %s", exc)
            return False

    def post_multiple_photos(self, image_paths: List[str], caption: Optional[str] = None) -> bool:
        """Upload and post multiple photos to Facebook page as a single post"""
        if not image_paths:
            logger.error("No images provided")
            return False

        if len(image_paths) > 10:
            logger.error("Facebook allows maximum 10 images per post")
            return False

        logger.info("Uploading %d photos to Facebook...", len(image_paths))

        # Step 1: Upload all photos without publishing
        photo_ids: List[str] = []
        for i, image_path in enumerate(image_paths, 1):
            if not os.path.exists(image_path):
                logger.error("Image file not found: %s", image_path)
                continue

            logger.debug("Uploading photo %d/%d: %s", i, len(image_paths), os.path.basename(image_path))

            url = f"{self.base_url}/{self.page_id}/photos"

            try:
                with open(image_path, "rb") as image_file:
                    files = {"source": image_file}
                    data = {
                        "access_token": self.access_token,
                        "published": "false"  # Don't publish yet
                    }

                    resp = self.session.post(url, files=files, data=data, timeout=60)

                    if resp.status_code == 200:
                        result = resp.json()
                        photo_id = result.get('id')
                        photo_ids.append(photo_id)
                        logger.info("Photo %d uploaded: %s", i, photo_id)
                    else:
                        error = resp.json().get("error", {}) if resp.content else {}
                        logger.error("Photo %d upload failed - Error %s: %s", i, error.get('code', ''), error.get('message', 'Request failed'))
                        continue

            except Exception as exc:
                logger.exception("Photo %d upload error: %s", i, exc)
                continue

        if not photo_ids:
            logger.error("No photos were uploaded successfully")
            return False

        # Step 2: Create a post with all uploaded photos
        logger.info("Creating post with %d photos...", len(photo_ids))

        # Format attached_media for the post
        attached_media = []
        for photo_id in photo_ids:
            attached_media.append({"media_fbid": photo_id})

        post_data: Dict[str, Any] = {
            "access_token": self.access_token,
            "attached_media": str(attached_media).replace("'", '"')  # Convert to JSON string
        }

        if caption:
            post_data["message"] = caption

        url = f"{self.base_url}/{self.page_id}/feed"

        try:
            resp = self.session.post(url, data=post_data, timeout=30)

            if resp.status_code == 200:
                result = resp.json()
                logger.info("Multi-photo post created! ID: %s", result.get('id'))
                return True
            else:
                error = resp.json().get("error", {}) if resp.content else {}
                logger.error("Multi-photo post failed - Error %s: %s", error.get('code', ''), error.get('message', 'Request failed'))

                # If post creation fails, try to clean up uploaded photos
                logger.info("Attempting to clean up uploaded photos...")
                for photo_id in photo_ids:
                    try:
                        delete_url = f"{self.base_url}/{photo_id}"
                        delete_data = {"access_token": self.access_token}
                        self.session.delete(delete_url, data=delete_data, timeout=10)
                    except Exception:
                        # Ignore cleanup errors
                        pass

                return False

        except Exception as exc:
            logger.exception("Multi-photo post error: %s", exc)
            return False

    def post_video(self, video_path: str, description: Optional[str] = None) -> bool:
        """Upload and post a video to Facebook page"""
        if not os.path.exists(video_path):
            logger.error("Video file not found: %s", video_path)
            return False

        url = f"{self.base_url}/{self.page_id}/videos"

        try:
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                data = {"access_token": self.access_token}
                if description:
                    data["description"] = description

                resp = self.session.post(url, files=files, data=data, timeout=300)

                if resp.status_code == 200:
                    result = resp.json()
                    logger.info("Video posted! ID: %s", result.get('id'))
                    return True
                else:
                    error = resp.json().get("error", {}) if resp.content else {}
                    logger.error("Video upload failed - Error %s: %s", error.get('code', ''), error.get('message', 'Request failed'))
                    return False

        except Exception as exc:
            logger.exception("Video upload error: %s", exc)
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
        
        # Example usage options
        print("\n🔸 Choose posting method:")
        print("1. Single text post")
        print("2. Single photo post")
        print("3. Multiple photos post")
        
        choice = input("Enter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            # Post message
            success = poster.post("Test post from Facebook script! 🚀")
        elif choice == "2":
            # Single photo (you would replace with actual image path)
            print("📸 For single photo, provide the image path:")
            image_path = input("Image path: ").strip()
            if image_path and os.path.exists(image_path):
                success = poster.post_photo(image_path, "Single photo test! 📸")
            else:
                print("❌ Invalid image path")
                return
        elif choice == "3":
            # Multiple photos (you would replace with actual image paths)
            print("📸 For multiple photos, provide image paths (comma-separated):")
            paths_input = input("Image paths: ").strip()
            if paths_input:
                image_paths = [path.strip() for path in paths_input.split(',')]
                # Filter valid paths
                valid_paths = [path for path in image_paths if os.path.exists(path)]
                if valid_paths:
                    success = poster.post_multiple_photos(valid_paths, "Multiple photos test! 📸✨")
                else:
                    print("❌ No valid image paths found")
                    return
            else:
                print("❌ No image paths provided")
                return
        else:
            print("❌ Invalid choice")
            return
        
        print("✅ Complete!" if success else "❌ Failed!")
        
    except ValueError as e:
        print(f"❌ Config error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
