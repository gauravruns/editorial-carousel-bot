import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemWarning, FileSystemLoader
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class SlideRenderer:
    """
    Headless browser renderer for generating high-definition carousel slides
    (1440x1800 aspect ratio) using Playwright and Jinja2.
    """
    def __init__(self, template_dir: Optional[str] = None, template_name: str = "slide_template.html"):
        if template_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(base_dir, "templates")
        
        self.template_dir = template_dir
        self.template_name = template_name
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template(template_name)

    def render_html(self, slide_data: Dict[str, Any], index: int, total_slides: int, brand_handle: str = "@publication") -> str:
        """
        Render slide data to an HTML string using the Jinja2 template.
        """
        slide = dict(slide_data)
        slide["index"] = index
        return self.template.render(
            slide=slide,
            total_slides=total_slides,
            brand_handle=brand_handle
        )

    async def render_slides_async(
        self,
        slides: List[Dict[str, Any]],
        output_dir: str,
        brand_handle: str = "@publication",
        width: int = 1440,
        height: int = 1800
    ) -> List[str]:
        """
        Render a list of slides asynchronously to HD PNG images.
        """
        os.makedirs(output_dir, exist_ok=True)
        output_paths = []
        total_slides = len(slides)

        logger.info(f"Starting rendering for {total_slides} slides at {width}x{height}...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": width, "height": height})
            page = await context.new_page()

            for i, slide_data in enumerate(slides, start=1):
                html_content = self.render_html(slide_data, i, total_slides, brand_handle)
                temp_html_path = os.path.join(output_dir, f"temp_slide_{i}.html")
                with open(temp_html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                await page.goto(f"file:///{os.path.abspath(temp_html_path).replace('\\', '/')}", wait_until="networkidle")
                
                # Let fonts and assets settle
                await asyncio.sleep(0.5)

                output_img_path = os.path.join(output_dir, f"slide_{i}.png")
                await page.screenshot(path=output_img_path, full_page=True)
                output_paths.append(output_img_path)
                logger.info(f"Rendered: {os.path.basename(output_img_path)}")

                # Clean up temporary HTML file
                try:
                    os.remove(temp_html_path)
                except OSError:
                    pass

            await browser.close()

        logger.info(f"Successfully rendered all {total_slides} slides to {output_dir}")
        return output_paths

    def render_deck(
        self,
        slides: List[Dict[str, Any]],
        output_dir: str,
        brand_handle: str = "@publication",
        width: int = 1440,
        height: int = 1800
    ) -> List[str]:
        """
        Synchronous convenience wrapper around render_slides_async.
        """
        return asyncio.run(
            self.render_slides_async(slides, output_dir, brand_handle, width, height)
        )
