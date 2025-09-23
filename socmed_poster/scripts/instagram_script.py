import dataclasses
import hashlib
import json
import logging
import os
import time
from typing import Optional, List, Dict

import requests
from dotenv import load_dotenv, find_dotenv
from PIL import Image  # 🔧 New import for resizing
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load .env from repository root if present
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class InstagramAPIError(Exception):
    """Raised when Instagram Graph API operations fail."""


class CloudinaryUploadError(Exception):
    """Raised when uploading to Cloudinary fails."""



class InstagramPoster:
    """Instagram direct posting via Graph API (Business/Creator Account)"""
    
    # Configuration constants
    API_VERSION = "v23.0"
    BASE_URL_TEMPLATE = "https://graph.facebook.com/{version}"
    CLOUDINARY_FOLDER = "socmed_poster"
    POLLING_TIMEOUT = 180
    INITIAL_POLL_INTERVAL = 5
    MAX_POLL_INTERVAL = 30

    def __init__(self):
        self.ig_id = os.getenv("INSTAGRAM_USER_ID")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.base_url = self.BASE_URL_TEMPLATE.format(version=self.API_VERSION)
        # Basic config validation
        if not self.ig_id or not self.access_token:
            raise ValueError("Missing INSTAGRAM_USER_ID or INSTAGRAM_ACCESS_TOKEN in environment")

        # Create a resilient requests session used by all network calls
        self.session = self._build_session(timeout=30)

        # Configure a module logger
        self.logger = logging.getLogger("instagram_poster")
        if not self.logger.handlers:
            # Basic console handler with INFO level by default
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _mask_sensitive_data(self, s: Optional[str]) -> str:
        if not s:
            return '(empty)'
        s = s.strip()
        if len(s) <= 6:
            return s
        return f"{s[:3]}...{s[-3:]}"

    def get_account_info(self) -> Optional[dict]:
        """Get Instagram account information (username, name).

        Returns a dict on success or None on failure. Handles transient
        network errors with a small retry loop and logs helpful messages.
        """
        self.logger.debug("Checking Instagram connection for ig_id=%s", self.ig_id)
        url = f"{self.base_url}/{self.ig_id}"
        params = {
            'fields': 'username,name',
            'access_token': self.access_token
        }

        for attempt in range(2):
            try:
                resp = self.session.get(url, params=params, timeout=20)
                if resp.status_code == 200:
                    result = resp.json()
                    if result:
                        self.logger.info("Instagram connection verified for: @%s", result.get('username', 'unknown'))
                    return result
                elif resp.status_code == 400:
                    # Bad request, likely wrong fields or token
                    self.logger.error("Failed to get Instagram account info (400): %s", resp.text)
                    break
                else:
                    self.logger.error("Failed to get Instagram account info: %s %s", resp.status_code, resp.text)
                    break

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                self.logger.warning("Transient network error getting Instagram account info (attempt %d): %s", attempt + 1, e)
                time.sleep(2 * (attempt + 1))
                continue
            except Exception as e:
                self.logger.exception("Unexpected error getting Instagram account info: %s", e)
                break

        return None

    # 🔧 New helper: validate & resize local images
    def _prepare_instagram_image(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Ensure image meets Instagram's aspect ratio requirements.
        If not, resize/pad it to 1080x1080 (safe square).
        """
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            w, h = img.size
            ratio = w / h

            if 0.8 <= ratio <= 1.91 and (320 <= w <= 1440) and (320 <= h <= 1440):
                # Already valid for IG
                return file_path

            # Otherwise, resize + pad to square
            if not output_path:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_igready.jpg"

            target_size = (1080, 1080)
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            new_img = Image.new("RGB", target_size, (255, 255, 255))
            new_img.paste(img, ((target_size[0] - img.size[0]) // 2,
                                (target_size[1] - img.size[1]) // 2))
            new_img.save(output_path, "JPEG", quality=90)

            self.logger.info("Fixed aspect ratio: saved IG-ready image at %s", output_path)
            return output_path

    def post_image(self, image_url: str, caption: str):
        """Publish an image post"""
        if not image_url.startswith('http'):
            # Local file → fix aspect ratio first
            image_url = self._prepare_instagram_image(image_url)
            uploaded = self._upload_to_cloudinary(image_url)
            if not uploaded:
                self.logger.error("Could not upload local file to Cloudinary.")
                return None
            image_url = uploaded

        container_url = f"{self.base_url}/{self.ig_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = self.session.post(container_url, data=payload)
        data = res.json()

        if "id" not in data:
            self.logger.error("Failed to create media container: %s", data)
            return None

        container_id = data["id"]
        self.logger.debug("Created media container: %s", container_id)

        publish_url = f"{self.base_url}/{self.ig_id}/media_publish"
        payload = {"creation_id": container_id, "access_token": self.access_token}
        res = self.session.post(publish_url, data=payload)
        result = res.json()

        if "id" in result:
            self.logger.info("Successfully posted! IG Post ID: %s", result['id'])
            return result["id"]
        else:
            self.logger.error("Failed to publish: %s", result)
            return None

    def post_carousel(self, image_paths: List[str], caption: str = "") -> Optional[str]:
        """Post a carousel with multiple images (2-10 images)"""
        if not image_paths or len(image_paths) < 2:
            self.logger.error("Carousel requires at least 2 images")
            return None

        if len(image_paths) > 10:
            self.logger.error("Instagram allows maximum 10 images in a carousel")
            return None
        self.logger.info("Creating carousel with %d images...", len(image_paths))

        children: List[str] = []
        for i, image_path in enumerate(image_paths):
            self.logger.debug("Processing image %d/%d: %s", i + 1, len(image_paths), os.path.basename(image_path))

            if not image_path.startswith('http'):
                image_path = self._prepare_instagram_image(image_path)  # 🔧 Fix aspect ratio first
                uploaded = self._upload_to_cloudinary(image_path)
                if not uploaded:
                    self.logger.error("Failed to upload image %d to Cloudinary", i + 1)
                    return None
                image_url = uploaded
            else:
                image_url = image_path

            container_url = f"{self.base_url}/{self.ig_id}/media"
            payload = {"image_url": image_url, "is_carousel_item": "true", "access_token": self.access_token}
            res = self.session.post(container_url, data=payload, timeout=30)
            data = res.json()

            if "id" not in data:
                self.logger.error("Failed to create container for image %d: %s", i + 1, data)
                return None

            children.append(data["id"])
            self.logger.debug("Created container %d: %s", i + 1, data['id'])

        # Carousel container + publish
        carousel_url = f"{self.base_url}/{self.ig_id}/media"
        payload = {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption,
                   "access_token": self.access_token}
        res = self.session.post(carousel_url, data=payload, timeout=30)
        data = res.json()

        if "id" not in data:
            self.logger.error("Failed to create carousel container: %s", data)
            return None

        carousel_id = data["id"]
        self.logger.debug("Created carousel container: %s", carousel_id)

        publish_url = f"{self.base_url}/{self.ig_id}/media_publish"
        payload = {"creation_id": carousel_id, "access_token": self.access_token}
        res = self.session.post(publish_url, data=payload, timeout=30)
        result = res.json()

        if "id" in result:
            self.logger.info("Successfully posted carousel! IG Post ID: %s", result['id'])
            return result["id"]
        else:
            self.logger.error("Failed to publish carousel: %s", result)
            return None

    def _upload_to_imgur(self, file_path: str) -> Optional[str]:
        """Upload a local image to Imgur anonymously and return the public URL.

        Requires `IMGUR_CLIENT_ID` in environment. Returns URL string or None.
        """
        client_id = os.getenv('IMGUR_CLIENT_ID')
        if not client_id:
            self.logger.warning("IMGUR_CLIENT_ID not set in environment. Cannot auto-upload local file to Imgur.")
            return None

        upload_url = 'https://api.imgur.com/3/image'
        try:
            with open(file_path, 'rb') as f:
                files = {'image': f}
                headers = {'Authorization': f'Client-ID {client_id}'}
                resp = self.session.post(upload_url, headers=headers, files=files, timeout=30)
            result = resp.json()
        except Exception as e:
            self.logger.exception("Error uploading to Imgur: %s", e)
            return None

        if not result.get('success'):
            self.logger.error("Imgur upload failed: %s", result)
            return None

        link = result.get('data', {}).get('link')
        self.logger.info("Uploaded to Imgur: %s", link)
        return link

    def _upload_to_cloudinary(self, file_path: str, resource_type: str = 'image') -> Optional[str]:
        """Upload a local file to Cloudinary and return the secure URL.

        Supports unsigned (preset) or signed uploads depending on env vars.
        Accepts `resource_type` of 'image' or 'video'.
        """
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        upload_preset = os.getenv('CLOUDINARY_UPLOAD_PRESET')

        # use _mask_sensitive_data helper for logging sensitive values

        if not cloud_name:
            self.logger.warning('Cloudinary not configured - CLOUDINARY_CLOUD_NAME missing.')
            return None

        use_unsigned = bool(upload_preset)
        use_signed = bool(api_key and api_secret and not upload_preset)

        if not use_unsigned and not use_signed:
            self.logger.warning('Cloudinary not configured properly.')
            self.logger.info("For unsigned uploads (recommended): set CLOUDINARY_UPLOAD_PRESET=%s", self._mask_sensitive_data(upload_preset))
            self.logger.info("For signed uploads: set CLOUDINARY_API_KEY=%s and CLOUDINARY_API_SECRET=%s", self._mask_sensitive_data(api_key), self._mask_sensitive_data(api_secret))
            return None

        url = f'https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload'
        if not os.path.exists(file_path):
            self.logger.error('Local file not found: %s', file_path)
            return None

        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                if use_unsigned:
                    data = {'upload_preset': upload_preset}
                    # For unsigned uploads, transformations must be handled by the upload preset
                    # The preset should be configured in Cloudinary dashboard with video settings
                    self.logger.info("Using unsigned Cloudinary upload with preset %s", self._mask_sensitive_data(upload_preset))
                    if resource_type == 'video':
                        self.logger.info("Note: Video transformations (H.264, MP4) should be configured in your Cloudinary upload preset")
                else:
                    timestamp = int(time.time())
                    params_to_sign = {'timestamp': timestamp, 'folder': 'socmed_poster'}
                    # For videos, add Instagram-compatible transformations
                    if resource_type == 'video':
                        params_to_sign.update({
                            'video_codec': 'h264',
                            'audio_codec': 'aac',
                            'format': 'mp4',
                            'fps': '30',
                            'bit_rate': '1000k'
                        })
                    params_str = '&'.join([f"{k}={v}" for k, v in sorted(params_to_sign.items())])
                    string_to_sign = params_str + api_secret
                    import hashlib
                    signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
                    data = {'api_key': api_key, 'timestamp': timestamp, 'signature': signature, 'folder': 'socmed_poster'}
                    # Add transformations to the data payload too
                    if resource_type == 'video':
                        data.update({
                            'video_codec': 'h264',
                            'audio_codec': 'aac',
                            'format': 'mp4',
                            'fps': '30',
                            'bit_rate': '1000k'
                        })
                    self.logger.info("Using signed Cloudinary upload with Instagram video transformations")

                resp = self.session.post(url, data=data, files=files, timeout=120)

            # Check HTTP status
            if resp.status_code != 200:
                self.logger.error('Cloudinary upload failed with status %s', resp.status_code)
                self.logger.debug('Cloudinary response body: %s', resp.text[:500])
                return None

            # Parse JSON response
            try:
                result = resp.json()
            except json.JSONDecodeError as json_err:
                self.logger.error('Cloudinary returned invalid JSON: %s', json_err)
                self.logger.debug('Cloudinary response body: %s', resp.text[:500])
                return None

        except Exception as e:
            self.logger.exception('Error uploading to Cloudinary: %s', e)
            return None

        # Cloudinary returns different fields for images vs videos
        secure = result.get('secure_url') or result.get('secure_url') or result.get('url')
        if not secure:
            self.logger.error('Cloudinary upload failed - no secure URL in response: %s', result)
            return None
        self.logger.info('Uploaded to Cloudinary: %s', secure)
        return secure

    def post_video(self, video_path: str, caption: str = "") -> Optional[str]:
        """Publish a video post to Instagram Business account.

        Local video files are uploaded to Cloudinary (or fallback to Imgur if configured),
        then a video media container is created and published.
        """
        if not video_path.startswith('http'):
            # Upload as video resource
            uploaded = self._upload_to_cloudinary(video_path, resource_type='video')
            if not uploaded:
                self.logger.warning("Could not upload local video to Cloudinary. Trying Imgur fallback...")
                uploaded = self._upload_to_imgur(video_path)
                if not uploaded:
                    self.logger.error("No upload method available for video. Aborting.")
                    return None
            video_url = uploaded
        else:
            video_url = video_path

        # Create video (REELS) container - Instagram Graph API requires 'REELS' for feed videos
        container_url = f"{self.base_url}/{self.ig_id}/media"
        payload = {
            # 'VIDEO' is deprecated and will return an error; use 'REELS' per API guidance
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }

        try:
            res = self.session.post(container_url, data=payload, timeout=120)
            data = res.json()
            if "id" not in data:
                self.logger.error("Failed to create video media container: %s", data)
                return None
            container_id = data["id"]
            self.logger.debug("Created video media container: %s", container_id)
        except Exception as e:
            self.logger.exception("Error creating video container: %s", e)
            return None

        # Poll the media container status until it's ready for publishing.
        # Instagram may take a short while to process uploaded videos. Use a
        # small backoff loop and a sensible timeout to avoid immediate publish
        # attempts which return 'media not ready' (error_subcode 2207027).
        check_url = f"{self.base_url}/{container_id}"
        wait_seconds = self.INITIAL_POLL_INTERVAL
        total_wait = 0
        max_wait = self.POLLING_TIMEOUT

        # We'll try requesting an extended field set first and fallback to a minimal
        # set if Graph complains about unsupported fields (some nodes don't expose processing_progress).
        fields_to_try = ['status_code,status,processing_progress', 'status_code,status']

        while total_wait < max_wait:
            last_error = None
            ready_for_publish = False
            
            for fields in fields_to_try:
                try:
                    status_resp = self.session.get(check_url, params={'fields': fields, 'access_token': self.access_token}, timeout=20)
                    try:
                        status_data = status_resp.json()
                    except Exception:
                        status_data = {'raw_text': status_resp.text}

                    # Debug: log the raw status payload so operator can see what's returned
                    self.logger.debug("Media status response for %s (fields=%s): %s", container_id, fields, status_data)

                    # If Graph returned an error object, capture and potentially retry with smaller field set
                    if isinstance(status_data, dict) and 'error' in status_data:
                        last_error = status_data['error']
                        # If it's an OAuthException complaining about a field, try the next (smaller) field set
                        self.logger.warning("Graph API error for fields=%s: %s", fields, last_error)
                        continue

                    # Accept a few possible readiness indicators
                    status_val = None
                    if isinstance(status_data, dict):
                        status_val = status_data.get('status_code') or status_data.get('status')

                    if status_val and str(status_val).upper() in ('FINISHED', 'READY', 'SUCCEEDED'):
                        self.logger.info("Media container %s ready for publish (status: %s)", container_id, status_val)
                        ready_for_publish = True
                        last_error = None
                        break
                    elif status_val and str(status_val).upper() == 'ERROR':
                        # Media failed to process - stop polling and return the error
                        error_msg = status_data.get('status', 'Unknown error')
                        self.logger.error("Media container %s failed processing: %s", container_id, error_msg)
                        self.logger.info("This often means the video format/codec doesn't meet Instagram requirements.")
                        self.logger.info("Try uploading an MP4 video with H.264 codec, 30fps max, and under 100MB.")
                        return None

                    # Not ready yet - break out of the fields loop and wait before retrying
                    self.logger.debug("Media %s not ready yet (fields=%s).", container_id, fields)
                    last_error = None
                    break

                except Exception as e:
                    last_error = {'message': str(e)}
                    self.logger.warning("Error checking media status for %s with fields=%s: %s", container_id, fields, e)

            # If ready for publish, break out of the main polling loop
            if ready_for_publish:
                break

            # If we saw an error for all tried field sets, print it for debugging
            if last_error:
                self.logger.warning("All field attempts failed for %s: %s", container_id, last_error)

            time.sleep(wait_seconds)
            total_wait += wait_seconds
            # small backoff
            if wait_seconds < self.MAX_POLL_INTERVAL:
                wait_seconds = min(wait_seconds + 5, self.MAX_POLL_INTERVAL)

        if total_wait >= max_wait:
            self.logger.error("Timed out waiting for media %s to be ready after %ss", container_id, max_wait)
            return None

        # Publish the container
        publish_url = f"{self.base_url}/{self.ig_id}/media_publish"
        payload = {"creation_id": container_id, "access_token": self.access_token}
        try:
            res = self.session.post(publish_url, data=payload, timeout=60)
            result = res.json()
            if "id" in result:
                self.logger.info("Successfully posted video! IG Post ID: %s", result['id'])
                return result["id"]
            else:
                self.logger.error("Failed to publish video: %s", result)
                return None
        except Exception as e:
            self.logger.exception("Error publishing video: %s", e)
            return None

    def _build_session(self, timeout: int = 30) -> requests.Session:
        """Create a requests.Session with retries configured for the poster."""
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("HEAD", "GET", "OPTIONS", "POST"))
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        # attach a default timeout attribute for convenience (not used by requests API directly)
        session.request_timeout = timeout  # type: ignore[attr-defined]
        return session
