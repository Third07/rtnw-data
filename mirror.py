# mirror.py
# RTNW JSON + asset mirror (Termux / desktop)
# Downloads known planner JSON from roworlddb.com/sea/
# Also probes common paths for missing packs and optional static assets.
#
# Usage:
#   python mirror.py              # skip existing files
#   python mirror.py --force      # re-download everything
#   python mirror.py --probe-js   # also try common JS/CSS candidate URLs

import os
import sys
import json
import urllib.request
import urllib.error

BASE = "https://www.roworlddb.com/sea/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RTNW-Mirror/1.1)",
    "Accept": "*/*",
}

FORCE = "--force" in sys.argv
PROBE_JS = "--probe-js" in sys.argv

# ---------------------------------------------------------------------------
# Known JSON endpoints (remote path relative to BASE → local path)
# Local layout matches a clean data/ tree for the GitHub Pages site.
# ---------------------------------------------------------------------------
FILES = [
    # --- Skill simulator ---
    (
        "skill-simulator/data/skills_index_en-US.json",
        "data/skills_index_en-US.json",
    ),
    (
        "skill-simulator/data/skills_index_zh-TW.json",
        "data/skills_index_zh-TW.json",
    ),
    (
        "skill-simulator/data/icon_paths.json",
        "data/icon_paths.json",
    ),
    # Rune planner data (hosted under skill-simulator on the live site)
    (
        "skill-simulator/data/engine_runes_en-US.json",
        "data/runes/engine_runes_en-US.json",
    ),
    (
        "skill-simulator/data/engine_runes_zh-TW.json",
        "data/runes/engine_runes_zh-TW.json",
    ),

    # --- Equipment ---
    (
        "equipment/data/equipment_en-US.json",
        "data/equipment/equipment_en-US.json",
    ),
    (
        "equipment/data/equipment_zh-TW.json",
        "data/equipment/equipment_zh-TW.json",
    ),

    # --- Cards ---
    (
        "card-simulator/data/handbook_cards_en-US.json",
        "data/cards/handbook_cards_en-US.json",
    ),
    (
        "card-simulator/data/handbook_cards_zh-TW.json",
        "data/cards/handbook_cards_zh-TW.json",
    ),
    (
        "card-simulator/data/card_fusion_simulator_en-US.json",
        "data/cards/card_fusion_simulator_en-US.json",
    ),
    (
        "card-simulator/data/card_fusion_simulator_zh-TW.json",
        "data/cards/card_fusion_simulator_zh-TW.json",
    ),

    # --- Monsters ---
    (
        "monster-album/data/monster_album_en-US.json",
        "data/monsters/monster_album_en-US.json",
    ),
    (
        "monster-album/data/monster_album_zh-TW.json",
        "data/monsters/monster_album_zh-TW.json",
    ),

    # --- Pets ---
    (
        "pet/data/pet_library_en-US.json",
        "data/pets/pet_library_en-US.json",
    ),
    (
        "pet/data/pet_library_zh-TW.json",
        "data/pets/pet_library_zh-TW.json",
    ),

    # --- Refine ---
    (
        "refine-simulator/data/refine_en-US.json",
        "data/refine/refine_en-US.json",
    ),
    (
        "refine-simulator/data/refine_zh-TW.json",
        "data/refine/refine_zh-TW.json",
    ),

    # --- Shop ---
    (
        "shop/data/shop_en-US.json",
        "data/shop/shop_en-US.json",
    ),
    (
        "shop/data/shop_zh-TW.json",
        "data/shop/shop_zh-TW.json",
    ),

    # --- Events ---
    (
        "events/data/events_en-US.json",
        "data/events/events_en-US.json",
    ),
    (
        "events/data/events_zh-TW.json",
        "data/events/events_zh-TW.json",
    ),

    # --- Apocalypse ---
    (
        "apocalypse-simulator/data/apocalypse_planner_en-US.json",
        "data/apocalypse/apocalypse_planner_en-US.json",
    ),
    (
        "apocalypse-simulator/data/apocalypse_planner_zh-TW.json",
        "data/apocalypse/apocalypse_planner_zh-TW.json",
    ),

    # --- Study / quiz ---
    (
        "study/data/guild_banquet_questions_en_us.json",
        "data/study/guild_banquet_questions_en_us.json",
    ),
    (
        "study/data/lucky_rabbit_questions_en_us.json",
        "data/study/lucky_rabbit_questions_en_us.json",
    ),
    (
        "study/data/scholar_exam_questions_en_us.json",
        "data/study/scholar_exam_questions_en_us.json",
    ),
    (
        "study/data/guild_banquet_questions_zh_tw.json",
        "data/study/guild_banquet_questions_zh_tw.json",
    ),
    (
        "study/data/lucky_rabbit_questions_zh_tw.json",
        "data/study/lucky_rabbit_questions_zh_tw.json",
    ),
    (
        "study/data/scholar_exam_questions_zh_tw.json",
        "data/study/scholar_exam_questions_zh_tw.json",
    ),

    # --- Maps ---
    (
        "map-simulator/data/map_index_en-US.json",
        "data/maps/map_index_en-US.json",
    ),
    (
        "map-simulator/data/map_index_zh-TW.json",
        "data/maps/map_index_zh-TW.json",
    ),
    (
        "map-simulator/data/map_monster_spawns_en-US.json",
        "data/maps/map_monster_spawns_en-US.json",
    ),
    (
        "map-simulator/data/map_monster_spawns_zh-TW.json",
        "data/maps/map_monster_spawns_zh-TW.json",
    ),
    (
        "map-simulator/data/interactive_placing_en-US/_index.json",
        "data/maps/interactive_placing/_index.json",
    ),
]

# Candidate paths for packs that may exist under different folder names.
# First successful download wins; failures are logged and skipped.
PROBE_JSON = [
    # Affix planner (path not confirmed on live site — probe several variants)
    (
        [
            "affix-simulator/data/affix_planner_en-US.json",
            "affix-simulator/data/engine_affixes_en-US.json",
            "affix-simulator/data/affixes_en-US.json",
            "affix_planner/data/affix_planner_en-US.json",
            "affix_planner/data/engine_affixes_en-US.json",
            "equipment/data/affix_planner_en-US.json",
            "equipment/data/engine_affixes_en-US.json",
            "skill-simulator/data/engine_affixes_en-US.json",
            "skill-simulator/data/affix_planner_en-US.json",
        ],
        "data/affix/affix_planner_en-US.json",
    ),
    (
        [
            "affix-simulator/data/affix_planner_zh-TW.json",
            "affix-simulator/data/engine_affixes_zh-TW.json",
            "affix_planner/data/affix_planner_zh-TW.json",
            "equipment/data/affix_planner_zh-TW.json",
            "skill-simulator/data/engine_affixes_zh-TW.json",
        ],
        "data/affix/affix_planner_zh-TW.json",
    ),
    # Alternate rune locations
    (
        [
            "rune-simulator/data/engine_runes_en-US.json",
            "rune_planner/data/engine_runes_en-US.json",
            "rune-simulator/data/runes_en-US.json",
        ],
        "data/runes/engine_runes_en-US.alt.json",
    ),
]

# Optional static asset probes (usually hashed bundles — most will 404).
# Kept so you can extend once you discover real hashed names from DevTools.
PROBE_STATIC = [
    # Hypothetical readable sources (unlikely on production SPA)
    ("skill-simulator/static/js/main.js", "assets/js/skill-simulator-main.js"),
    ("skill_planner/static/js/main.js", "assets/js/skill-planner-main.js"),
    ("rune_planner/static/js/main.js", "assets/js/rune-planner-main.js"),
    ("affix_planner/static/js/main.js", "assets/js/affix-planner-main.js"),
    ("equipment/static/js/main.js", "assets/js/equipment-main.js"),
    ("card-simulator/static/js/main.js", "assets/js/cards-main.js"),
    ("monster-album/static/js/main.js", "assets/js/monsters-main.js"),
    ("pet/static/js/main.js", "assets/js/pet-main.js"),
    ("shop/static/js/main.js", "assets/js/shop-main.js"),
    ("events/static/js/main.js", "assets/js/events-main.js"),
    ("apocalypse-simulator/static/js/main.js", "assets/js/apocalypse-main.js"),
    ("study/static/js/main.js", "assets/js/study-main.js"),
    ("map-simulator/static/js/main.js", "assets/js/map-main.js"),
]


def download(remote, local, quiet_404=False):
    """Download remote (relative to BASE) to local path. Returns True on success."""
    os.makedirs(os.path.dirname(local) or ".", exist_ok=True)

    if os.path.exists(local) and not FORCE:
        print("✓ Skip", local)
        return True

    url = BASE + remote if not remote.startswith("http") else remote

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
            # Reject empty / HTML error pages that return 200
            ctype = (r.headers.get("Content-Type") or "").lower()
            if "text/html" in ctype and not remote.endswith((".html", ".htm")):
                raise ValueError("Got HTML instead of expected asset")

        with open(local, "wb") as f:
            f.write(data)

        print("✓", local, "(%d bytes)" % len(data))
        return True

    except urllib.error.HTTPError as e:
        if quiet_404 and e.code == 404:
            return False
        print("✗", remote, "→ HTTP", e.code)
        return False
    except Exception as e:
        if quiet_404:
            return False
        print("✗", remote)
        print(" ", e)
        return False


def download_first(candidates, local):
    """Try candidates in order; stop on first success."""
    if os.path.exists(local) and not FORCE:
        print("✓ Skip", local)
        return True
    for remote in candidates:
        if download(remote, local, quiet_404=True):
            return True
    print("✗ (all probes failed for)", local)
    for remote in candidates:
        print("   tried:", remote)
    return False


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def download_jobs():
    print("\n=== Job data (en-US + zh-TW if index present) ===\n")
    locales = [
        ("data/skills_index_en-US.json", "en-US", "data/jobs_en-US"),
        ("data/skills_index_zh-TW.json", "zh-TW", "data/jobs_zh-TW"),
    ]
    for index_file, locale, out_dir in locales:
        if not os.path.exists(index_file):
            print("· No index for", locale, "— skip jobs")
            continue
        index = load_json(index_file)
        jobs = index.get("jobs") or index
        for job_id in sorted(jobs.keys(), key=lambda x: int(x) if str(x).isdigit() else 0):
            download(
                f"skill-simulator/data/jobs_{locale}/{job_id}.json",
                f"{out_dir}/{job_id}.json",
            )


def download_interactive_maps():
    print("\n=== Interactive map tiles / placing files ===\n")
    map_index = "data/maps/interactive_placing/_index.json"
    if not os.path.exists(map_index):
        print("_index.json not found. Skipping interactive map files.")
        return

    files = load_json(map_index)
    names = []
    if isinstance(files, list):
        names = files
    elif isinstance(files, dict):
        # support { "files": [...] } or { "name": ... }
        if "files" in files and isinstance(files["files"], list):
            names = files["files"]
        else:
            names = list(files.keys())

    for name in names:
        name = str(name).lstrip("/")
        download(
            f"map-simulator/data/interactive_placing_en-US/{name}",
            f"data/maps/interactive_placing/{name}",
        )


def main():
    print("\n=== RTNW mirror ===")
    print("BASE:", BASE)
    print("FORCE:", FORCE)
    print("PROBE_JS:", PROBE_JS)
    print()

    print("=== Known JSON files ===\n")
    ok = fail = 0
    for remote, local in FILES:
        if download(remote, local):
            ok += 1
        else:
            fail += 1

    print("\n=== Probe optional / unknown JSON (affix, alt runes) ===\n")
    for candidates, local in PROBE_JSON:
        if download_first(candidates, local):
            ok += 1
        else:
            fail += 1

    download_jobs()
    download_interactive_maps()

    if PROBE_JS:
        print("\n=== Probe static JS candidates (expect many 404s) ===\n")
        print("Tip: open roworlddb in DevTools → Network → JS to find real hashed bundle names,")
        print("then add those exact paths to PROBE_STATIC in this script.\n")
        for remote, local in PROBE_STATIC:
            download(remote, local, quiet_404=False)

    print("\n===================================")
    print("Mirror finished.")
    print("Known JSON attempts: success-ish count depends on skip/404s above.")
    print()
    print("Notes:")
    print(" • engine_runes_*.json is the Rune planner pack (under skill-simulator).")
    print(" • Affix planner JSON path is unknown; probes try common names.")
    print(" • Production JS is usually hashed (e.g. main.a1b2c3.js). Use DevTools")
    print("   to capture real URLs, then append them to PROBE_STATIC or FILES.")
    print(" • Rebuild your own UI against the JSON — do not rely on their minified SPA.")
    print("===================================\n")


if __name__ == "__main__":
    main()
