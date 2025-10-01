import os
import requests
import logging
from dotenv import load_dotenv
from time import sleep

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

    def __init__(self, access_token=None, person_id=None, session=None):
        """Initialize the poster.

        access_token: LinkedIn member access token (required)
        person_id: numeric LinkedIn person id (required)
        session: optional requests.Session for connection reuse/testing
        """
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        # require LINKEDIN_PERSON_ID (numeric id) — we will not call /me automatically
        self.person_id = person_id or os.getenv('LINKEDIN_PERSON_ID')
        self.api_url = "https://api.linkedin.com/v2"
        self.session = session or requests.Session()

        if not self.access_token:
            raise ValueError("LinkedIn access token not found in environment variables (LINKEDIN_ACCESS_TOKEN)")
        if not self.person_id:
            raise ValueError("LinkedIn person id not found in environment variables (LINKEDIN_PERSON_ID).\nProvide the numeric person id; this module will not call /me automatically.")
        # validate numeric person id to avoid invalid URNs
        if not str(self.person_id).isdigit():
            raise ValueError("LINKEDIN_PERSON_ID must be numeric")

    def _headers(self):
        # X-Restli-Protocol-Version is recommended for UGC endpoints
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def verify_credentials(self, check_remote: bool = False) -> bool:
        """Verify configuration and optionally call LinkedIn /me to validate the token.

        check_remote: if True, performs a GET /me to validate the token and return True
        only if the call succeeds (200). Default False to avoid calling /me.
        """
        if not self.access_token:
            logger.error("Missing LINKEDIN_ACCESS_TOKEN")
            return False
        if not self.person_id:
            logger.error("Missing LINKEDIN_PERSON_ID")
            return False
        if not check_remote:
            logger.info("Configuration present (token and person id). Note: no /me verification performed.")
            return True

        # perform a safe /me call to validate the token
        try:
            resp = self.session.get(f"{self.api_url}/me", headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                logger.info("Remote verification succeeded")
                return True
            logger.error("Remote verification failed: %s %s", resp.status_code, resp.text)
            return False
        except requests.RequestException as exc:
            logger.error("Remote verification error: %s", exc)
            return False

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

        # Simple retry logic for transient failures (3 attempts)
        attempts = 3
        backoff = 1
        for attempt in range(1, attempts + 1):
            try:
                resp = self.session.post(f"{self.api_url}/ugcPosts", json=post_data, headers=self._headers(), timeout=10)
                if resp.status_code in (200, 201):
                    logger.info("Posted to LinkedIn successfully (status=%s)", resp.status_code)
                    return True
                # For 4xx errors don't retry (permission/validation issues)
                if 400 <= resp.status_code < 500:
                    logger.error("LinkedIn post failed (client error): %s %s\nHeaders: %s", resp.status_code, resp.text, dict(resp.headers))
                    return False
                # server error -> retry
                logger.warning("LinkedIn post temporary failure (attempt %s/%s): %s", attempt, attempts, resp.status_code)
            except requests.RequestException as exc:
                logger.warning("LinkedIn posting exception (attempt %s/%s): %s", attempt, attempts, exc)

            if attempt < attempts:
                sleep(backoff)
                backoff *= 2

        logger.error("LinkedIn post failed after %s attempts", attempts)
        return False