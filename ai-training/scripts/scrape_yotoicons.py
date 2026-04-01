"""
Scrape Yoto Player icon images using a headless browser (Playwright).

Since yotoicons.com uses bot protection that blocks simple HTTP requests,
this script uses a real headless browser to load the pages and download
the icon images.

Requirements:
  pip install playwright
  playwright install chromium

Usage:
  # Scrape all animal icons:
  python scrape_yotoicons.py --tag animals --output ../dataset/images

  # Scrape multiple tags:
  python scrape_yotoicons.py --tag animals --tag nature --output ../dataset/images

  # Scrape all icons (all pages):
  python scrape_yotoicons.py --all --output ../dataset/images

  # Limit pages scraped:
  python scrape_yotoicons.py --tag animals --max-pages 5 --output ../dataset/images
"""

import argparse
import asyncio
import os
import time
from pathlib import Path
from urllib.parse import urljoin

from playwright.async_api import async_playwright


BASE_URL = "https://www.yotoicons.com"


async def scrape_icons(tag: str, output_dir: str, max_pages: int = 100):
    """Scrape icon images from yotoicons.com for a given tag."""
    os.makedirs(output_dir, exist_ok=True)
    downloaded = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        current_page = 1
        while current_page <= max_pages:
            if tag:
                url = f"{BASE_URL}/icons?tag={tag}&page={current_page}"
            else:
                url = f"{BASE_URL}/icons?page={current_page}"

            print(f"\nLoading page {current_page}: {url}")

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"  Error loading page: {e}")
                break

            # Wait for images to load
            await page.wait_for_timeout(2000)

            # Find all icon images on the page
            # Try common patterns for icon image elements
            image_urls = await page.evaluate("""
                () => {
                    const urls = new Set();

                    // Look for img tags with icon-related classes or in icon containers
                    document.querySelectorAll('img').forEach(img => {
                        const src = img.src || img.dataset.src || img.getAttribute('data-lazy-src');
                        if (src && !src.includes('logo') && !src.includes('avatar')
                            && !src.includes('placeholder')) {
                            urls.add(src);
                        }
                    });

                    // Also check for background images in icon cards/containers
                    document.querySelectorAll('[style*="background-image"]').forEach(el => {
                        const match = el.style.backgroundImage.match(/url\\(['"]*(.+?)['"]*\\)/);
                        if (match) urls.add(match[1]);
                    });

                    // Check canvas elements (some pixel art sites render to canvas)
                    // We can't extract these directly, but note them
                    const canvasCount = document.querySelectorAll('canvas').length;

                    return {
                        imageUrls: Array.from(urls),
                        canvasCount: canvasCount,
                        // Get page HTML snippet for debugging
                        bodyClasses: document.body.className,
                        iconContainerCount: document.querySelectorAll(
                            '.icon, .icon-card, .icon-item, [class*="icon"], [class*="card"]'
                        ).length,
                    };
                }
            """)

            urls = image_urls.get("imageUrls", [])
            canvas_count = image_urls.get("canvasCount", 0)
            container_count = image_urls.get("iconContainerCount", 0)

            print(f"  Found: {len(urls)} images, {canvas_count} canvases, {container_count} icon containers")

            if not urls and canvas_count == 0:
                print("  No more icons found. Stopping.")
                break

            # Download each image
            for img_url in urls:
                try:
                    # Make the URL absolute if needed
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    elif img_url.startswith("/"):
                        img_url = urljoin(BASE_URL, img_url)

                    # Download via the browser context (inherits cookies/session)
                    response = await context.request.get(img_url)

                    if response.ok:
                        body = await response.body()
                        ext = ".png"
                        content_type = response.headers.get("content-type", "")
                        if "jpeg" in content_type or "jpg" in content_type:
                            ext = ".jpg"
                        elif "webp" in content_type:
                            ext = ".webp"
                        elif "gif" in content_type:
                            ext = ".gif"

                        filename = f"yoto_{tag or 'all'}_{downloaded:04d}{ext}"
                        filepath = os.path.join(output_dir, filename)

                        with open(filepath, "wb") as f:
                            f.write(body)

                        downloaded += 1
                        print(f"    [{downloaded}] Saved: {filename}")

                except Exception as e:
                    print(f"    Error downloading {img_url}: {e}")

            # Check if there's a next page
            has_next = await page.evaluate("""
                () => {
                    const nextBtn = document.querySelector(
                        'a[rel="next"], .next, [class*="next"], .pagination a:last-child'
                    );
                    return nextBtn !== null && !nextBtn.classList.contains('disabled');
                }
            """)

            if not has_next:
                print("  No more pages.")
                break

            current_page += 1
            # Be polite - don't hammer the server
            await page.wait_for_timeout(1500)

        await browser.close()

    print(f"\nDone! Downloaded {downloaded} icons to: {output_dir}")
    return downloaded


async def scrape_with_download_buttons(tag: str, output_dir: str, max_pages: int = 100):
    """
    Alternative approach: click on each icon and use the download button.
    Use this if the direct image scraping doesn't capture the right files.
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
            accept_downloads=True,
        )
        page = await context.new_page()

        url = f"{BASE_URL}/icons?tag={tag}" if tag else f"{BASE_URL}/icons"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # Take a screenshot for debugging
        screenshot_path = os.path.join(output_dir, "_debug_screenshot.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"  Debug screenshot saved: {screenshot_path}")

        # Print page structure for debugging
        structure = await page.evaluate("""
            () => {
                const info = {
                    title: document.title,
                    allImages: Array.from(document.querySelectorAll('img')).map(img => ({
                        src: img.src,
                        alt: img.alt,
                        width: img.naturalWidth,
                        height: img.naturalHeight,
                        classes: img.className,
                    })),
                    allLinks: Array.from(document.querySelectorAll('a[href*="download"], a[href*="icon"]'))
                        .slice(0, 20)
                        .map(a => ({ href: a.href, text: a.textContent.trim() })),
                    mainContent: document.querySelector('main, #content, .content, [role="main"]')
                        ?.innerHTML?.substring(0, 2000) || 'no main content found',
                };
                return info;
            }
        """)

        print(f"\n  Page title: {structure.get('title')}")
        print(f"  Images found: {len(structure.get('allImages', []))}")
        for img in structure.get("allImages", [])[:10]:
            print(f"    - {img.get('src', 'no src')} ({img.get('width')}x{img.get('height')}) [{img.get('alt')}]")

        print(f"\n  Download/icon links: {len(structure.get('allLinks', []))}")
        for link in structure.get("allLinks", [])[:10]:
            print(f"    - {link.get('href')} [{link.get('text')}]")

        await browser.close()

    return downloaded


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Yoto Player icons from yotoicons.com"
    )
    parser.add_argument(
        "--tag", action="append", default=[],
        help="Tag to scrape (e.g., 'animals'). Can be specified multiple times.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Scrape all icons (no tag filter)",
    )
    parser.add_argument(
        "--output", default="../dataset/images",
        help="Output directory for downloaded images",
    )
    parser.add_argument(
        "--max-pages", type=int, default=100,
        help="Maximum number of pages to scrape per tag",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Run in debug mode: take screenshots and print page structure",
    )

    args = parser.parse_args()

    tags = args.tag if args.tag else [None] if args.all else None

    if tags is None:
        print("Specify a tag with --tag or use --all to scrape everything.")
        print("Example: python scrape_yotoicons.py --tag animals --output ../dataset/images")
        return

    for tag in tags:
        tag_label = tag or "all"
        print(f"\n{'='*50}")
        print(f"Scraping: {tag_label}")
        print(f"{'='*50}")

        if args.debug:
            asyncio.run(scrape_with_download_buttons(tag, args.output, args.max_pages))
        else:
            asyncio.run(scrape_icons(tag, args.output, args.max_pages))


if __name__ == "__main__":
    main()
