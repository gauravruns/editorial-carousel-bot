import os
import logging
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class CatboxUploader:
    """
    Uploads rendered slide images to Catbox.moe for public CDN hosting
    compatible with Meta Graph API image ingestion.
    """
    API_URL = "https://catbox.moe/user/api.php"

    def __init__(self, userhash: Optional[str] = None):
        self.userhash = userhash or os.getenv("CATBOX_USERHASH")

    def upload_file(self, file_path: str) -> str:
        """
        Upload a single image file to Catbox and return the public URL.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Uploading {os.path.basename(file_path)} to Catbox CDN...")
        data = {"reqtype": "fileupload"}
        if self.userhash:
            data["userhash"] = self.userhash

        with open(file_path, "rb") as f:
            files = {"fileToUpload": (os.path.basename(file_path), f)}
            response = requests.post(self.API_URL, data=data, files=files, timeout=60)

        if response.status_code == 200 and response.text.startswith("http"):
            public_url = response.text.strip()
            logger.info(f"Successfully uploaded: {public_url}")
            return public_url
        else:
            raise RuntimeError(f"Catbox upload failed (HTTP {response.status_code}): {response.text}")

    def upload_batch(self, file_paths: List[str]) -> List[str]:
        """
        Upload a batch of slide images in sequence and return list of public URLs.
        """
        urls = []
        for path in file_paths:
            url = self.upload_file(path)
            urls.append(url)
        return urls
