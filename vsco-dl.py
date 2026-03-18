import re
import requests
import json
import urllib.request
import os
import sys
import time
import random
import argparse
import cloudscraper

def download_item(scraper, username, file_url, content_type, downloaded_urls):
    if not file_url:
        return

    # Remove URL parameters.
    clean_url = file_url.split("?")[0]

    # Bypass image resizer to obtain the original resolution.
    if "cdn-cgi/image/" in clean_url:
        match = re.search(r'cdn-cgi/image/[^/]+/(.*)', clean_url)
        if match:
            clean_url = "https://im.vsco.co/" + match.group(1)

    # Ensure the URL has a valid protocol.
    if clean_url.startswith("//"):
        clean_url = "https:" + clean_url
    elif not clean_url.startswith("http"):
        clean_url = "https://" + clean_url

    # Avoid duplicate downloads within the same session.
    if clean_url in downloaded_urls:
        return
    downloaded_urls.add(clean_url)

    is_video = ".mp4" in clean_url.lower()
    if is_video and "photo" in content_type:
        return
    if not is_video and "video" in content_type:
        return

    # Extract the filename from the URL.
    parts = clean_url.split("/")
    if len(parts) >= 2:
        fname = f"{parts[-2]}_{parts[-1]}"
    else:
        fname = parts[-1]

    dir_name = username + "/"
    path = dir_name + fname

    if os.path.exists(path):
        return

    # Attempt download with retries for HTTP 429 errors.
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = scraper.get(clean_url, stream=True)

            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {fname}")
                break

            elif response.status_code == 429:
                print(f"Rate limited on image. Cooling down for 15 seconds (Attempt {attempt + 1}/{max_retries}).")
                time.sleep(15)
                continue

            else:
                print(f"Failed (Status {response.status_code}): {clean_url}")
                break

        except Exception as e:
            print(f"Failed to download {clean_url}: {e}")
            break


def main():
    parser = argparse.ArgumentParser(description="Download all images and videos from a VSCO user via API")
    parser.add_argument('username', action="store", help="Username of VSCO user")
    parser.add_argument('pages', action="store", help="Number of pages (batches of 14) to download. Default is 999.", type=int, nargs='?', default=999)
    parser.add_argument('--content', action="store", help="Option to download only videos (video) or photos (photo)", default="CONTENT")

    args = parser.parse_args()

    print(f"Initializing scraper for {args.username}...")

    # Initialize cloudscraper.
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'firefox', 'platform': 'linux', 'desktop': True}
    )

    # Fetch initial page for site ID and Bearer token.
    profile_url = f"https://vsco.co/{args.username}/gallery"
    r = scraper.get(profile_url)

    if r.status_code == 404:
        print("Invalid username (404 Not Found).")
        sys.exit(1)
    elif r.status_code == 403:
        print("Blocked by Cloudflare (403 Forbidden).")
        sys.exit(1)

    matches = re.findall(r'window\.__PRELOADED_STATE__ = (.*?)</script>', r.text, re.DOTALL)
    if not matches:
        print("Could not find the internal JSON state.")
        sys.exit(1)

    raw_json = matches[0].strip()
    if raw_json.endswith(';'):
        raw_json = raw_json[:-1]

    raw_json = raw_json.replace(':undefined', ':null')

    try:
        state = json.loads(raw_json)
        site_id = state["sites"]["siteByUsername"][args.username]["site"]["id"]
        bearer_token = state["users"]["currentUser"]["tkn"]
    except Exception as e:
        print(f"Failed to extract credentials: {e}")
        sys.exit(1)

    print(f"Found site_id ({site_id}) and API token.")
    os.makedirs(args.username, exist_ok=True)

    # Begin API requests for media.
    api_headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json",
        "User-Agent": scraper.headers["User-Agent"]
    }

    cursor = ""
    current_page = 0
    downloaded_urls = set()

    while current_page < args.pages:
        api_url = f"https://vsco.co/api/3.0/medias/profile?site_id={site_id}&limit=14"
        if cursor:
            api_url += f"&cursor={cursor}"

        response = scraper.get(api_url, headers=api_headers)

        # Handle API rate limiting specifically.
        if response.status_code == 429:
            print(f"API Rate limit hit. Sleeping for 15 seconds before retrying page {current_page + 1}.")
            time.sleep(15)
            continue

        if response.status_code != 200:
            print(f"API Request failed with status: {response.status_code}")
            break

        data = response.json()
        media_array = data.get("media") or data.get("medias", [])

        if not media_array:
            print(f"No media found on page {current_page + 1}.")
            break

        for item in media_array:
            item_str = json.dumps(item)

            video_matches = re.findall(r'"([^"]*\.mp4[^"]*)"', item_str)
            image_matches = re.findall(r'"([^"]*im\.vsco\.co/[^"]*|[^"]*cdn-cgi/image/[^"]*)"', item_str)

            file_url = None

            if video_matches and "photo" not in args.content:
                file_url = video_matches[0]
            elif image_matches and "video" not in args.content:
                file_url = image_matches[0]

            if not file_url:
                continue

            download_item(scraper, args.username, file_url, args.content, downloaded_urls)

            # Add a delay between downloads to prevent rate limiting.
            time.sleep(random.uniform(0.5, 1.5))

        new_cursor = data.get("next_cursor") or data.get("nextCursor")

        if not new_cursor or new_cursor == cursor:
            break

        cursor = new_cursor
        current_page += 1

        # Add a delay between fetching pages.
        time.sleep(random.uniform(2.0, 4.0))

    if "video" in args.content and not os.listdir(args.username):
        os.rmdir(args.username)
        print("No videos found.")
    else:
        print("Download complete.")


if __name__ == "__main__":
    main()
