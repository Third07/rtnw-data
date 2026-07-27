import os
from collections import Counter

FAILED = "data/logs/failed_images.txt"

if not os.path.exists(FAILED):
    print("failed_images.txt not found.")
    exit()

folders = Counter()
extensions = Counter()

total = 0

with open(FAILED, encoding="utf-8") as f:
    for line in f:

        line = line.strip()

        if not line:
            continue

        total += 1

        if "/" in line:
            folder = line.split("/", 1)[0]
        else:
            folder = "(root)"

        folders[folder] += 1

        ext = os.path.splitext(line)[1].lower()

        if ext:
            extensions[ext] += 1

print("\n==========================")
print("FAILED IMAGE ANALYSIS")
print("==========================")
print("Total Failed:", total)

print("\nFolders")
print("--------------------------")

for folder, count in folders.most_common():
    print(f"{folder:<25} {count}")

print("\nExtensions")
print("--------------------------")

for ext, count in extensions.most_common():
    print(f"{ext:<10} {count}")

print("\nTop 50 Failed Paths")
print("--------------------------")

shown = 0

with open(FAILED, encoding="utf-8") as f:
    for line in f:

        line = line.strip()

        if not line:
            continue

        print(line)

        shown += 1

        if shown >= 50:
            break