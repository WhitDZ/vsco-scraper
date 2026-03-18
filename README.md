# vsco-dl — VSCO Media Downloader

Download original, high-resolution images and videos from a VSCO user profile using Python. This is an updated and maintained fork of the original script, modified to bypass modern Cloudflare protections and API rate limits.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Updated fork based on the original work by sdushantha


## Features

- High Resolution: Bypasses CDN resizing to download the maximum quality original media files.
- Protection Bypass: Utilizes `cloudscraper` to seamlessly handle Cloudflare bot protections and 403 errors.
- Rate Limit Handling: Automatically detects HTTP 429 errors, pauses, and retries to prevent IP bans.
- Media Filtering: Flexible options to download only photos, only videos, or both.
- Duplicate Prevention: Remembers what you've downloaded and skips existing files locally.


## Important disclaimer

This tool interacts with VSCO's internal API. Downloading large volumes of media rapidly can result in temporary IP bans (Rate Limiting). The script has built-in delays to prevent this, but use it responsibly. You can change the delays but default doesn't get rate limited.


## Quick start

1) Clone the repository to your machine
   ```bash
    https://github.com/WhitDZ/vsco-scraper.git
    cd vsco-scraper
   ```

3) Install the required dependencies (Requires Python 3.6 or higher)
   ```bash
    pip install requests cloudscraper
   ```

5) Run the downloader
   ```bash
    python vsco_dl.py <username>
   ```


## Using the downloader

**Basic Syntax:**
  ```bash
    python vsco_dl.py <username> [pages] [--content photo|video]
  ```

**Examples:**

- Download everything (photos and videos) from a user:
  ```bash
    python vsco_dl.py example_user
  ```
  
- Download ONLY videos from a specific user:
  ```bash
    python vsco_dl.py example_user --content video
  ```
  
- Download ONLY photos from the first 5 pages of a user's profile:
  ```bash
    python vsco_dl.py example_user 5 --content photo
  ```

## Troubleshooting

- Invalid username (404 Not Found)
  - The profile does not exist or the username was typed incorrectly.
- Blocked by Cloudflare (403 Forbidden)
  - VSCO updated their Cloudflare settings. Ensure `cloudscraper` is up to date (`pip install --upgrade cloudscraper`).
- Rate limited on image (429 Too Many Requests)
  - You are downloading too fast. The script will automatically pause for 15 seconds and retry. No action is needed.



## Credits & License

Originally created by [sdushantha](https://github.com/sdushantha/vsco-dl). This fork updates the scraping logic, Cloudflare bypass, and dependency usage to restore full functionality.

This project is licensed under the MIT License.
