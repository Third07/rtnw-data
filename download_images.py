import os
import time
import random
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

IMAGE_FOLDERS = [
    "",
    "achievement/",
    "action/",
    "activity/",
    "activitylabel/",
    "adventureevent/",
    "attr/",
    "card/",
    "ember/",
    "equip/",
    "head/",
    "item/",
    "job/",
    "map/",
    "monster/",
    "mount/",
    "npc/",
    "pet/",
    "shadowequip/",
    "skill/",
    "ui/",
    "weapon/",
    "zhujiemian/",
]

BASE = "https://www.roworlddb.com/media/images/"
LIST_FILE = "data/cache/images.txt"
SAVE_DIR = "data/images"

THREADS = 10
RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

lock = Lock()

downloaded = 0
skipped = 0
failed = 0

os.makedirs("data/logs", exist_ok=True)


def log(file, text):
    with lock:
        with open(file, "a", encoding="utf-8") as f:
            f.write(text + "\n")


def download(path, total, index):

    global downloaded, skipped, failed

    path = path.strip().lstrip("/")

    if not path:
        return

    if path.startswith("media/images/"):
        path = path[13:]

    # Already contains folder
    candidates = [path]

    # Only filename? Try every known folder
    if "/" not in path:
        candidates = [folder + path for folder in IMAGE_FOLDERS]

    for candidate in candidates:

        url = BASE + candidate
        local = os.path.join(SAVE_DIR, candidate)

        os.makedirs(os.path.dirname(local), exist_ok=True)

        if os.path.exists(local):
            with lock:
                skipped += 1
                print(f"[{index}/{total}] SKIP {candidate}")
            return

        for attempt in range(RETRIES):

            try:

                req = urllib.request.Request(url, headers=HEADERS)

                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()

                with open(local, "wb") as f:
                    f.write(data)

                with lock:
                    downloaded += 1
                    print(f"[{index}/{total}] OK   {candidate}")

                log("data/logs/downloaded_images.txt", candidate)
                return

            except urllib.error.HTTPError:
                # Try next folder
                break

            except Exception:
                if attempt == RETRIES - 1:
                    time.sleep(0.5)

    with lock:
        failed += 1
        print(f"[{index}/{total}] FAIL {path}")

    log("data/logs/failed_images.txt", path)


if not os.path.exists(LIST_FILE):
    print("images.txt not found.")
    exit()

with open(LIST_FILE, encoding="utf-8") as f:
    images = sorted(set(
        line.strip()
        for line in f
        if line.strip()
    ))

total = len(images)

print()
print("==============================")
print("RTNW Image Mirror")
print("==============================")
print("Images :", total)
print("Threads:", THREADS)
print()

with ThreadPoolExecutor(max_workers=THREADS) as executor:

    for i, img in enumerate(images, 1):

        executor.submit(download, img, total, i)

print()
print("==============================")
print("Finished")
print("==============================")
print("Downloaded :", downloaded)
print("Skipped    :", skipped)
print("Failed     :", failed)
print()
print("Logs:")
print("data/logs/downloaded_images.txt")
print("data/logs/failed_images.txt")
