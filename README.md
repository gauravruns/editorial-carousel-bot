# Editorial Carousel Bot 🚀

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/rendered%20with-Playwright-green.svg)](https://playwright.dev/)
[![Meta Graph API](https://img.shields.io/badge/Meta%20Graph%20API-v21.0-blue.svg)](https://developers.facebook.com/docs/instagram-platform/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated, production-grade pipeline to programmatically generate, render, host, and publish high-impact editorial carousels directly to Instagram Business accounts using **Playwright**, **Jinja2**, and the **Meta Graph API**.

---

## 🌟 Key Highlights

- **Pixel-Perfect Headless Rendering**: Renders slides at ultra-high resolution (1440×1800 HD portrait, 4:5 aspect ratio) with hardware-accelerated headless Chromium via Playwright.
- **Institutional Dark-Mode Aesthetic**: Designed with an editorial theme—featuring deep canvas tones (`#0D0D0D`), high-contrast typography (`Inter` & `JetBrains Mono`), and electric green accents (`#00FF88`).
- **Dynamic Layout & Data Components**: Built-in templates for structured editorial lists, key metric callouts, custom highlight tags, and background imagery overlays.
- **Zero-Friction Asset Staging**: Headless CDN asset staging via Catbox for seamless Meta Graph API ingestion without interactive auth or complex cloud storage setup.
- **Robust Meta Graph API Orchestration**: Fully automated multi-stage publishing pipeline (individual slide media containers, asynchronous readiness polling, parent `CAROUSEL` packaging, and live publication with captions and permalink retrieval).

---

## 📁 Project Architecture

```text
editorial-carousel-bot/
├── core/
│   ├── __init__.py           # Package exports
│   ├── renderer.py           # Playwright + Jinja2 HTML-to-image rendering engine
│   ├── uploader.py           # CDN asset uploader
│   ├── publisher.py          # Meta Graph API carousel orchestrator
│   └── pipeline.py           # End-to-end coordinated pipeline
├── templates/
│   └── slide_template.html   # 1440x1800 editorial dark-mode HTML/CSS template
├── examples/
│   ├── sample_deck.json      # Complete sample deck with metrics and points
│   └── run_example.py        # Standalone programmatic example script
├── main.py                   # Command-line interface (CLI)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/gauravruns/editorial-carousel-bot.git
cd editorial-carousel-bot

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your Meta Graph API credentials:

```bash
cp .env.example .env
```

```dotenv
# Meta Graph API (Instagram Business Account)
IG_ACCESS_TOKEN=your_never_expiring_meta_user_or_page_token
IG_USER_ID=your_instagram_business_account_id

# Optional CDN userhash
CATBOX_USERHASH=
```

---

## 💻 Usage

### CLI Commands

#### Render Slides Locally (Preview Mode)
Render your JSON deck to 1440×1800 PNG images without publishing:

```bash
python main.py render --deck examples/sample_deck.json --output ./output
```

#### Render & Publish Live to Instagram
Execute the full end-to-end pipeline (render -> upload to CDN -> bundle -> publish):

```bash
python main.py publish --deck examples/sample_deck.json --caption "Deep dive into macroeconomic liquidity cycles. #macro #finance #markets"
```

---

### Python API

You can also integrate the pipeline directly into your custom data science, research, or content workflows:

```python
from core.renderer import SlideRenderer
from core.uploader import CatboxUploader
from core.publisher import InstagramPublisher

slides = [
    {
        "category": "EXECUTIVE BRIEF",
        "tag": "MARKET SHIFT",
        "title": "The New Regime in <span class=\"highlight\">Capital Markets</span>",
        "subtitle": "How rate volatility is reshaping asset allocation.",
        "metrics": [
            {"value": "$315T", "label": "Global Debt", "subtext": "New all-time high"}
        ]
    }
]

# 1. Render
renderer = SlideRenderer()
images = renderer.render_deck(slides, output_dir="./output", brand_handle="@publication")

# 2. Upload
uploader = CatboxUploader()
public_urls = uploader.upload_batch(images)

# 3. Publish
publisher = InstagramPublisher()
result = publisher.publish_carousel(public_urls, caption="Market update for institutional investors.")
print(f"Post live at: {result['permalink']}")
```

---

## 📄 Slide Deck Schema

Slide decks are authored as JSON files with support for headline tags, highlighted spans (`<span class="highlight">`), bullet points, and high-impact metric cards:

```json
{
  "brand_handle": "@yourbrand",
  "slides": [
    {
      "category": "MARKET ANALYSIS",
      "tag": "LIQUIDITY",
      "title": "Understanding the <span class=\"highlight\">Yield Curve</span>",
      "subtitle": "Key observations across fixed income maturities.",
      "metrics": [
        {
          "value": "4.65%",
          "label": "10Y Benchmark",
          "subtext": "Critical technical resistance"
        }
      ],
      "points": [
        {
          "title": "Term Premium Expansion",
          "description": "Investors are demanding higher compensation for holding longer-dated bonds."
        }
      ]
    }
  ]
}
```

---

## 🛡️ License

Distributed under the [MIT License](LICENSE).
