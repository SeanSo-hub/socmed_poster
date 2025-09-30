import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LinkedInPoster:
    """Minimal helper for posting simple text UGC to LinkedIn.

    Notes:
    - Requires LINKEDIN_ACCESS_TOKEN in environment.
    - LINKEDIN_PERSON_ID is optional; if not provided the class will try to fetch it from /me.
    """

    def __init__(self, access_token=None, person_id=None):
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        # require LINKEDIN_PERSON_ID (numeric id) — we will not call /me automatically
        self.person_id = person_id or os.getenv('LINKEDIN_PERSON_ID')
        self.api_url = "https://api.linkedin.com/v2"

        if not self.access_token:
            raise ValueError("LinkedIn access token not found in environment variables (LINKEDIN_ACCESS_TOKEN)")
        if not self.person_id:
            raise ValueError("LinkedIn person id not found in environment variables (LINKEDIN_PERSON_ID).\nProvide the numeric person id; this module will not call /me automatically.")

    def _headers(self):
        # X-Restli-Protocol-Version is recommended for UGC endpoints
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def verify_credentials(self):
        """Verify that required configuration is present.

        NOTE: This method does NOT call /me. If you want to validate the token against
        LinkedIn's /me endpoint, run a separate one-off check — this module intentionally
        avoids using /me so it works in environments where /me is restricted.
        """
        if not self.access_token:
            logger.error("Missing LINKEDIN_ACCESS_TOKEN")
            return False
        if not self.person_id:
            logger.error("Missing LINKEDIN_PERSON_ID")
            return False
        # We can't reliably verify token scopes without calling LinkedIn member endpoints.
        logger.info("Configuration present (token and person id). Note: no /me verification performed.")
        return True

    def post(self, message):
        """Post simple text content as a UGC post.

        Returns True on success, False otherwise.
        """
        if not self.person_id:
            logger.error("Cannot post: LINKEDIN_PERSON_ID not set")
            return False

        post_data = {
            "author": f"urn:li:person:{self.person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        try:
            resp = requests.post(f"{self.api_url}/ugcPosts", json=post_data, headers=self._headers(), timeout=10)
            if resp.status_code in (200, 201):
                logger.info("Posted to LinkedIn successfully (status=%s)", resp.status_code)
                return True
            logger.error("LinkedIn post failed: %s %s", resp.status_code, resp.text)
            return False
        except requests.RequestException as exc:
            logger.error("LinkedIn posting error: %s", exc)
            return False