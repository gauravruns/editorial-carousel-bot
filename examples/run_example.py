"""Quickstart example demonstrating how to run the Editorial Carousel Bot."""

import json
from pathlib import Path
from core.pipeline import CarouselPipeline

def run():
    # Load sample deck definition
    deck_file = Path(__file__).parent / "sample_deck.json"
    with open(deck_file, "r", encoding="utf-8") as f:
        deck_data = json.load(f)

    # Initialize pipeline
    pipeline = CarouselPipeline()

    # Run in dry-run mode (renders slides and uploads to CDN, but does not publish to Instagram)
    print("Starting sample carousel pipeline in dry-run mode...\n")
    result = pipeline.run(
        deck_data=deck_data,
        output_dir="examples/rendered_output",
        dry_run=True
    )

    print("\nSample run completed!")
    print(f"Rendered {len(result['rendered_files'])} slides.")
    print(f"CDN URLs:")
    for idx, url in enumerate(result['image_urls'], start=1):
        print(f"  Slide {idx}: {url}")

if __name__ == "__main__":
    run()
