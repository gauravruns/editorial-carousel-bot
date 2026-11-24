import json
from pathlib import Path
from typing import Dict, Any, Optional
from .renderer import SlideRenderer
from .uploader import upload_to_cdn
from .publisher import InstagramPublisher

class CarouselPipeline:
    """Orchestrates rendering, CDN uploading, and Instagram publishing."""

    def __init__(self, template_path: Optional[str] = None):
        if template_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            template_path = str(base_dir / "templates" / "slide_template.html")
        self.renderer = SlideRenderer(template_path=template_path)

    def run(
        self,
        deck_data: Dict[str, Any],
        output_dir: str = "rendered_slides",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Executes the full carousel pipeline.

        Args:
            deck_data: Dictionary containing 'caption' and 'slides'.
            output_dir: Local directory to store rendered PNGs.
            dry_run: If True, renders and uploads slides but skips Instagram publishing.
        """
        slides = deck_data.get("slides", [])
        caption = deck_data.get("caption", "")

        if not slides:
            raise ValueError("deck_data must contain a non-empty 'slides' list.")

        print(f"=== Step 1: Rendering {len(slides)} slides via Playwright ===")
        rendered_files = self.renderer.render_slides(slides, output_dir)

        print(f"\n=== Step 2: Uploading {len(rendered_files)} slides to public CDN ===")
        image_urls = []
        for idx, file_path in enumerate(rendered_files, start=1):
            url = upload_to_cdn(file_path)
            image_urls.append(url)
            print(f"  - Slide {idx} CDN URL: {url}")

        if dry_run:
            print("\n[DRY RUN] Skipping Instagram Graph API publish step.")
            return {
                "status": "dry_run_success",
                "rendered_files": rendered_files,
                "image_urls": image_urls,
                "caption": caption
            }

        print("\n=== Step 3: Publishing Carousel to Instagram via Meta Graph API ===")
        publisher = InstagramPublisher()
        publish_result = publisher.publish_carousel(image_urls, caption)

        return {
            "status": "published",
            "rendered_files": rendered_files,
            "image_urls": image_urls,
            "post_id": publish_result.get("post_id"),
            "permalink": publish_result.get("permalink")
        }
