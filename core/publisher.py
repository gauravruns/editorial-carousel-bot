import os
import time
import logging
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class InstagramPublisher:
    """
    Production-grade publishing client for Instagram Business accounts
    via the Meta Graph API.
    """
    GRAPH_API_VERSION = "v21.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self, access_token: Optional[str] = None, ig_user_id: Optional[str] = None):
        self.access_token = access_token or os.getenv("IG_ACCESS_TOKEN")
        self.ig_user_id = ig_user_id or os.getenv("IG_USER_ID")

        if not self.access_token or not self.ig_user_id:
            raise ValueError(
                "Missing required credentials: IG_ACCESS_TOKEN and IG_USER_ID must be set "
                "either in the environment or passed directly."
            )

    def create_item_container(self, image_url: str) -> str:
        """
        Create an individual media container for a carousel item.
        """
        url = f"{self.BASE_URL}/{self.ig_user_id}/media"
        payload = {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": self.access_token
        }
        resp = requests.post(url, data=payload, timeout=30)
        res_data = resp.json()

        if "id" not in res_data:
            raise RuntimeError(f"Failed to create item container for {image_url}: {res_data}")
        
        container_id = res_data["id"]
        logger.info(f"Created item container: {container_id}")
        return container_id

    def wait_for_container(self, container_id: str, max_retries: int = 15, delay_s: int = 3) -> bool:
        """
        Poll container status until status_code == 'FINISHED'.
        """
        url = f"{self.BASE_URL}/{container_id}"
        params = {
            "fields": "status_code",
            "access_token": self.access_token
        }

        for attempt in range(max_retries):
            resp = requests.get(url, params=params, timeout=20)
            data = resp.json()
            status = data.get("status_code")
            if status == "FINISHED":
                return True
            elif status == "ERROR":
                raise RuntimeError(f"Container {container_id} failed with error status: {data}")
            time.sleep(delay_s)

        logger.warning(f"Container {container_id} status poll timed out. Continuing...")
        return True

    def create_carousel_container(self, children_ids: List[str], caption: str) -> str:
        """
        Create parent CAROUSEL container grouping all child slide containers.
        """
        url = f"{self.BASE_URL}/{self.ig_user_id}/media"
        payload = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": self.access_token
        }
        resp = requests.post(url, data=payload, timeout=30)
        res_data = resp.json()

        if "id" not in res_data:
            raise RuntimeError(f"Failed to create parent carousel container: {res_data}")

        parent_id = res_data["id"]
        logger.info(f"Created parent carousel container: {parent_id}")
        return parent_id

    def publish_container(self, creation_id: str) -> Dict[str, Any]:
        """
        Publish the parent carousel container live to Instagram.
        """
        url = f"{self.BASE_URL}/{self.ig_user_id}/media_publish"
        payload = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        resp = requests.post(url, data=payload, timeout=30)
        res_data = resp.json()

        if "id" not in res_data:
            raise RuntimeError(f"Failed to publish media: {res_data}")

        post_id = res_data["id"]
        logger.info(f"Successfully published post! Post ID: {post_id}")
        return res_data

    def get_permalink(self, post_id: str) -> Optional[str]:
        """
        Fetch the public Instagram permalink for a published post ID.
        """
        url = f"{self.BASE_URL}/{post_id}"
        params = {
            "fields": "permalink",
            "access_token": self.access_token
        }
        resp = requests.get(url, params=params, timeout=20)
        return resp.json().get("permalink")

    def publish_carousel(self, image_urls: List[str], caption: str) -> Dict[str, Any]:
        """
        End-to-end automated publishing flow:
        1. Create containers for all slides
        2. Wait for processing
        3. Bundle into parent carousel
        4. Publish to Instagram
        """
        if not 2 <= len(image_urls) <= 10:
            raise ValueError(f"Instagram carousels require between 2 and 10 slides. Got {len(image_urls)}.")

        logger.info(f"Beginning automated carousel publication for {len(image_urls)} slides...")
        child_ids = []
        for i, url in enumerate(image_urls, start=1):
            logger.info(f"Creating container for slide {i}/{len(image_urls)}...")
            c_id = self.create_item_container(url)
            child_ids.append(c_id)
            time.sleep(1)

        # Wait for all child containers to finish processing
        for c_id in child_ids:
            self.wait_for_container(c_id)

        # Create parent carousel
        logger.info("Creating parent carousel bundle...")
        parent_id = self.create_carousel_container(child_ids, caption)
        self.wait_for_container(parent_id)

        # Publish live
        logger.info("Publishing carousel live to Instagram...")
        result = self.publish_container(parent_id)
        post_id = result.get("id")
        permalink = self.get_permalink(post_id) if post_id else None

        return {
            "post_id": post_id,
            "permalink": permalink,
            "parent_container_id": parent_id,
            "child_containers": child_ids,
            "slide_count": len(image_urls)
        }
