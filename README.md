vsco-dl

A command-line tool to download original, high-resolution images and videos from a VSCO user profile.

This repository provides an updated and maintained version of the original vsco-dl script by sdushantha, modified to handle recent changes in the VSCO API and Cloudflare protections.

Features

High Resolution: Bypasses CDN resizing to download the original media files.

Protection Bypass: Utilizes cloudscraper to handle Cloudflare bot protections.

Rate Limit Handling: Automatically detects HTTP 429 errors, pauses, and retries to prevent IP bans.

Media Filtering: Options to download only photos, only videos, or both.

Duplicate Prevention: Skips files that have already been downloaded to the local directory.

Requirements

Requires Python 3.6 or higher. Install the required dependencies using pip:

pip install requests cloudscraper


Usage

Basic Syntax:

python vsco_dl.py <username> [pages] [--content photo|video]


Examples:

Download all media from a specific user:

python vsco_dl.py example_user


Download only videos from a specific user:

python vsco_dl.py example_user --content video


Download only photos from the first 5 pages of a user's profile:

python vsco_dl.py example_user 5 --content photo


Credits

Originally created by sdushantha. This fork updates the scraping logic and dependency usage to restore functionality.
