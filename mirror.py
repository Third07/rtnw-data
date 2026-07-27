# mirror.py
#
# RTNW Data Mirror (Termux)
#
# Features
# - Downloads entry JSON files
# - Scans JavaScript for JSON references
# - Downloads discovered JSON automatically
# - Preserves folder structure
# - Easy to extend later

import os
import re
import json
import urllib.request
from urllib.parse import urljoin

BASE = "https://www.roworlddb.com/sea/"

OUTPUT = "data"

ENTRY_FILES = [
    "skill-simulator/data/skills_index_en-US.json",
    "skill-simulator/data/icon_paths.json",
]

ENTRY_JS = [
    "skill_planner/simulator.js",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    req = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(req) as r:
        data = r.read()

    with open(path, "wb") as f:
        f.write(data)

    print("✓", path)


def fetch_text(url):
    req = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8", "ignore")


print("Downloading entry files...\n")

for f in ENTRY_FILES:
    download(
        urljoin(BASE, f),
        os.path.join(OUTPUT, os.path.basename(f))
    )

print("\nScanning JavaScript...\n")

json_urls = set()

for js in ENTRY_JS:

    text = fetch_text(urljoin(BASE, js))

    matches = re.findall(r'["\']([^"\']+\.json[^"\']*)["\']', text)

    for m in matches:

        if m.startswith("http"):
            json_urls.add(m)
        else:
            json_urls.add(urljoin(BASE, m))

print("Found", len(json_urls), "JSON references.\n")

for url in sorted(json_urls):

    rel = url.replace(BASE, "")

    path = os.path.join(OUTPUT, rel)

    try:
        download(url, path)
    except Exception as e:
        print("✗", url)
        print(e)

print("\nMirror complete.")
