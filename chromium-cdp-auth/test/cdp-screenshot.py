import os
import sys
import time
from playwright.sync_api import sync_playwright

if len(sys.argv) < 4 or len(sys.argv) > 5:
    print(f"Usage: {sys.argv[0]} <cdp-url> <url-to-screenshot> <screenshot_filename> [token]", file=sys.stderr)
    print(f"Example: {sys.argv[0]} https://spring-dream-p5wxwwl0.fra.unikraft.app https://google.com 1.png my-token", file=sys.stderr)
    print(f"Token can also be set via CDP_TOKEN environment variable.", file=sys.stderr)
    sys.exit(1)

cdp_url = sys.argv[1]
screenshot_url = sys.argv[2]
screenshot_filename = sys.argv[3]
token = sys.argv[4] if len(sys.argv) == 5 else os.environ.get("CDP_TOKEN", "")

if token:
    separator = "&" if "?" in cdp_url else "?"
    cdp_url = f"{cdp_url}{separator}token={token}"

t_start = time.time()

try:
    p = sync_playwright().start()

    t_connect = time.time()
    browser = p.chromium.connect_over_cdp(cdp_url)
    t_connected = time.time()

    # Open a new browser page.
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    new_page = browser.new_page(user_agent=USER_AGENT)
    new_page.set_extra_http_headers(
            {"sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="24"'}
        )

    t_goto = time.time()
    new_page.goto(screenshot_url)
    t_loaded = time.time()

    MAX_SCREENSHOT_HEIGHT = 16384
    dimensions = new_page.evaluate(
        """
        () => {
            return {
               width: document.documentElement.scrollWidth,
                height: document.documentElement.scrollHeight,
                deviceScaleFactor: window.devicePixelRatio,
            }
        }
    """
    )

    # Set the viewport to the full page size (up to a maximum height of MAX_ALLOWED_HEIGHT)
    new_page.set_viewport_size(
            {
                "width": dimensions["width"],
                "height": min(dimensions["height"], MAX_SCREENSHOT_HEIGHT),
            }
        )

    # Take a single screenshot of the entire page
    screenshot = new_page.screenshot()

    with open(screenshot_filename, "wb") as stream:
        stream.write(screenshot)

    t_end = time.time()
    print(f"OK {screenshot_filename}: connect={t_connected - t_connect:.2f}s goto={t_loaded - t_goto:.2f}s total={t_end - t_start:.2f}s")

    new_page.close()
    browser.close()
    p.stop()
except Exception as e:
    t_end = time.time()
    print(f"FAIL {screenshot_filename}: {e} (after {t_end - t_start:.2f}s)", file=sys.stderr)
    sys.exit(1)
