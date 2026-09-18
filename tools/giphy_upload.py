#!/usr/bin/env python3
"""Upload the 30 Gigi office GIFs to Giphy.

API key is read ONLY from the GIPHY_API_KEY environment variable and is
never written to disk, logs, or results. Results JSON holds ids/urls only.

Usage: GIPHY_API_KEY=... python3 giphy_upload.py
"""
import json
import os
import sys
import time

import requests

GIF_DIR = os.path.expanduser("~/workspace/your_files/gigi_otter")
RESULTS = os.path.expanduser(os.environ.get(
    "GIPHY_RESULTS", "~/workspace/gif-station/giphy_upload_results.json"))

# Canonical hashtag: every upload from the vault carries this first, so one
# search pulls up all of our work on Giphy.
CANONICAL_TAG = "xcessive"
UPLOAD_URL = "https://upload.giphy.com/v1/gifs"

STATES = [
    "idle", "working", "listening", "speaking", "thinking", "success",
    "alert", "tired", "bitching", "pushing_to_github", "deploying",
    "debugging", "facepalm", "laughing", "smug", "drinking_coffee",
    "eating_snack", "dancing", "sleeping", "surprised", "shrugging",
    "scheming", "panic", "salute", "celebrating", "gaming", "rebooting",
    "overheating", "flexing", "goodbye",
]


def upload(state, api_key):
    path = os.path.join(GIF_DIR, f"gigi_office_{state}.gif")
    if not os.path.exists(path):
        return {"error": f"file missing: {path}"}
    tags = f"{CANONICAL_TAG}, gigi, sovran, otter, " + state.replace("_", " ")
    for attempt in (1, 2):
        try:
            with open(path, "rb") as fh:
                resp = requests.post(
                    UPLOAD_URL,
                    data={"api_key": api_key, "tags": tags},
                    files={"file": (f"gigi_office_{state}.gif", fh, "image/gif")},
                    timeout=120,
                )
            body = resp.json()
            if resp.status_code == 200 and body.get("meta", {}).get("status") == 200:
                gid = body["data"]["id"]
                return {"id": gid, "url": f"https://giphy.com/gifs/{gid}"}
            err = {"error": f"attempt {attempt}: HTTP {resp.status_code} {body.get('meta')}"}
        except Exception as e:  # noqa: BLE001
            err = {"error": f"attempt {attempt}: {type(e).__name__}: {e}"}
        time.sleep(5)
    return err


def main():
    api_key = os.environ.get("GIPHY_API_KEY")
    if not api_key:
        print("GIPHY_API_KEY env var is required", file=sys.stderr)
        sys.exit(1)
    results = {}
    for i, state in enumerate(STATES, 1):
        print(f"[{i:2d}/30] uploading {state} ...", flush=True)
        results[state] = upload(state, api_key)
        r = results[state]
        print(f"           -> {'OK ' + r['url'] if 'url' in r else 'FAIL ' + r['error']}",
              flush=True)
        time.sleep(2)  # stay well under the rate limit
    with open(RESULTS, "w") as fh:
        json.dump(results, fh, indent=2)
    ok = sum(1 for r in results.values() if "url" in r)
    print(f"done: {ok}/30 uploaded; results in giphy_upload_results.json")


if __name__ == "__main__":
    main()
