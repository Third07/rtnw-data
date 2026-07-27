# mirror.py
# RTNW JSON Mirror (Termux)
# Downloads all known JSON data except icons.

import os
import json
import urllib.request

BASE = "https://www.roworlddb.com/sea/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FILES = [
    (
        "skill-simulator/data/skills_index_en-US.json",
        "data/skills/skills_index_en-US.json"
    ),
    (
        "skill-simulator/data/icon_paths.json",
        "data/skills/icon_paths.json"
    ),
    (
        "skill-simulator/data/engine_runes_en-US.json",
        "data/skills/engine_runes_en-US.json"
    ),

    (
        "equipment/data/equipment_en-US.json",
        "data/equipment/equipment_en-US.json"
    ),

    (
        "card-simulator/data/handbook_cards_en-US.json",
        "data/cards/handbook_cards_en-US.json"
    ),

    (
        "card-simulator/data/card_fusion_simulator_en-US.json",
        "data/cards/card_fusion_simulator_en-US.json"
    ),

    (
        "monster-album/data/monster_album_en-US.json",
        "data/monsters/monster_album_en-US.json"
    ),

    (
        "pet/data/pet_library_en-US.json",
        "data/pets/pet_library_en-US.json"
    ),

    (
        "refine-simulator/data/refine_en-US.json",
        "data/refine/refine_en-US.json"
    ),

    (
        "shop/data/shop_en-US.json",
        "data/shop/shop_en-US.json"
    ),

    (
        "events/data/events_en-US.json",
        "data/events/events_en-US.json"
    ),

    (
        "apocalypse-simulator/data/apocalypse_planner_en-US.json",
        "data/apocalypse/apocalypse_planner_en-US.json"
    ),

    (
        "study/data/guild_banquet_questions_en_us.json",
        "data/study/guild_banquet_questions_en_us.json"
    ),

    (
        "study/data/lucky_rabbit_questions_en_us.json",
        "data/study/lucky_rabbit_questions_en_us.json"
    ),

    (
        "study/data/scholar_exam_questions_en_us.json",
        "data/study/scholar_exam_questions_en_us.json"
    ),

    (
        "map-simulator/data/map_index_en-US.json",
        "data/maps/map_index_en-US.json"
    ),

    (
        "map-simulator/data/map_monster_spawns_en-US.json",
        "data/maps/map_monster_spawns_en-US.json"
    ),

    (
        "map-simulator/data/interactive_placing_en-US/_index.json",
        "data/maps/interactive_placing/_index.json"
    ),
]


def download(remote, local):

    os.makedirs(os.path.dirname(local), exist_ok=True)

    if os.path.exists(local):
        print("✓ Skip", local)
        return

    url = BASE + remote

    try:

        req = urllib.request.Request(url, headers=HEADERS)

        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()

        with open(local, "wb") as f:
            f.write(data)

        print("✓", local)

    except Exception as e:

        print("✗", remote)
        print(" ", e)


print("\n=== Downloading Known JSON Files ===\n")

for remote, local in FILES:
    download(remote, local)


print("\n=== Downloading Job Data ===\n")

index_file = "data/skills/skills_index_en-US.json"

if os.path.exists(index_file):

    with open(index_file, encoding="utf-8") as f:
        index = json.load(f)

    jobs = index.get("jobs", {})

    for job_id in sorted(jobs.keys(), key=int):

        download(
            f"skill-simulator/data/jobs_en-US/{job_id}.json",
            f"data/skills/jobs_en-US/{job_id}.json"
        )

else:

    print("skills_index_en-US.json not found.")


print("\n=== Downloading Interactive Map Files ===\n")

map_index = "data/maps/interactive_placing/_index.json"

if os.path.exists(map_index):

    with open(map_index, encoding="utf-8") as f:
        files = json.load(f)

    if isinstance(files, list):

        for name in files:

            download(
                f"map-simulator/data/interactive_placing_en-US/{name}",
                f"data/maps/interactive_placing/{name}"
            )

    elif isinstance(files, dict):

        for name in files.keys():

            download(
                f"map-simulator/data/interactive_placing_en-US/{name}",
                f"data/maps/interactive_placing/{name}"
            )

else:

    print("_index.json not found. Skipping interactive map files.")


print("\n===================================")
print("Mirror completed.")
print("===================================")