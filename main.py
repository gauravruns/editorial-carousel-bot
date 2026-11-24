#!/usr/bin/env python3
"""
Editorial Carousel Bot - CLI Entrypoint

Automated rendering and publishing of editorial carousels to Instagram.
"""

import os
import json
import argparse
import logging
from dotenv import load_dotenv

from core.renderer import SlideRenderer
from core.uploader import CatboxUploader
from core.publisher import InstagramPublisher

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("carousel-bot")

def load_deck(deck_path: str):
    with open(deck_path, "r", encoding="utf-8") as f:
        return json.load(f)

def cmd_render(args):
    deck = load_deck(args.deck)
    slides = deck.get("slides", [])
    brand_handle = args.brand or deck.get("brand_handle", "@publication")
    output_dir = args.output or os.path.join(os.getcwd(), "output")

    renderer = SlideRenderer()
    rendered_paths = renderer.render_deck(slides, output_dir, brand_handle)
    print(f"\n[SUCCESS] Rendered {len(rendered_paths)} slides to: {output_dir}")
    for p in rendered_paths:
        print(f"  - {p}")
    return rendered_paths

def cmd_publish(args):
    deck = load_deck(args.deck)
    slides = deck.get("slides", [])
    brand_handle = args.brand or deck.get("brand_handle", "@publication")
    output_dir = args.output or os.path.join(os.getcwd(), "output")

    # Step 1: Render slides
    logger.info("Rendering slides...")
    renderer = SlideRenderer()
    rendered_paths = renderer.render_deck(slides, output_dir, brand_handle)

    # Step 2: Upload to CDN
    logger.info("Uploading slides to public CDN...")
    uploader = CatboxUploader()
    public_urls = uploader.upload_batch(rendered_paths)

    caption = args.caption or deck.get("default_caption", f"New editorial analysis by {brand_handle}. #markets #macro #research")

    # Step 3: Publish via Instagram Graph API
    logger.info("Publishing to Instagram...")
    publisher = InstagramPublisher()
    res = publisher.publish_carousel(public_urls, caption)

    print(f"\n[SUCCESS] Published Carousel Successfully!")
    print(f"Post ID:   {res.get('post_id')}")
    if res.get('permalink'):
        print(f"Permalink: {res.get('permalink')}")

def main():
    parser = argparse.ArgumentParser(description="Editorial Carousel Bot - Automated Instagram Publishing Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Render command
    p_render = subparsers.add_parser("render", help="Render slides to HD PNGs")
    p_render.add_argument("--deck", required=True, help="Path to JSON deck configuration")
    p_render.add_argument("--output", default="output", help="Output directory for rendered PNGs")
    p_render.add_argument("--brand", help="Brand handle override (e.g. @myhandle)")
    p_render.set_defaults(func=cmd_render)

    # Publish command
    p_pub = subparsers.add_parser("publish", help="Render, host, and publish carousel live to Instagram")
    p_pub.add_argument("--deck", required=True, help="Path to JSON deck configuration")
    p_pub.add_argument("--output", default="output", help="Output directory for rendered PNGs")
    p_pub.add_argument("--caption", help="Instagram caption text")
    p_pub.add_argument("--brand", help="Brand handle override (e.g. @myhandle)")
    p_pub.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
