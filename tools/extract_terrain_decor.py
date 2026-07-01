#!/usr/bin/env python3
"""
extract_terrain_decor.py — (re)génère 30 décors depuis Glow_Terrain.png vers
02_Asset/runtime/<clé>.png  (buissons, buissons fleuris, fleurs, rochers, souches).

Atlas Glow_Terrain.png : grille 8×8, cellule 512×512, fond transparent.
Mapping clé moteur → (ligne, colonne) — voir tools/PROGRESS.md pour la carte des 64 cases.

Usage :
  python3 tools/extract_terrain_decor.py           # dry-run
  python3 tools/extract_terrain_decor.py --write     # écrit les PNG runtime + clés
"""
import sys
from PIL import Image
import asset_lib as A

G = 512
MAP = {
    "bush1": (0, 0), "bush2": (0, 3), "bush3": (0, 4), "bush4": (0, 6), "bush5": (1, 2), "bush6": (0, 1),
    "bushF1": (0, 2), "bushF2": (0, 5), "bushF3": (1, 0), "bushF4": (1, 1), "bushF5": (1, 3), "bushF6": (0, 7),
    "flower1": (4, 5), "flower2": (4, 6), "flower3": (4, 7), "flower4": (5, 0), "flower5": (5, 1), "flower6": (5, 2),
    "rock1": (1, 4), "rock2": (1, 5), "rock3": (1, 6), "rock4": (1, 7), "rock5": (2, 0), "rock6": (2, 1),
    "stump1": (2, 2), "stump2": (2, 3), "stump3": (4, 2), "stump4": (2, 4), "stump5": (2, 7), "stump6": (4, 3),
}


def main(write):
    atlas = Image.open(A.ASSET / "Glow_Terrain.png").convert("RGBA")
    html = A.HTML.read_text(encoding="utf-8") if write else None
    added_total = []
    for key, (r, c) in MAP.items():
        spr = A.extract_sprite(atlas, (c * G, r * G, c * G + G, r * G + G), keep_ratio=0.05)
        if spr is None:
            print("  !! VIDE", key, (r, c)); sys.exit(1)
        print("  %-9s R%dC%d  %dx%d%s" % (key, r, c, spr.width, spr.height, "" if write else "  (dry-run)"))
        if write:
            html, added = A.register_key(html, key, spr)
            if added:
                added_total.append(key)

    if not write:
        print("\nDry-run — rien écrit. Relance avec --write pour appliquer.")
        return
    A.HTML.write_text(html, encoding="utf-8")
    A.rebuild_manifest()
    print("\n30 PNG écrits. Nouvelles clés PACK :", added_total or "(aucune, re-skin pur)")
    print("Audit :", A.audit())
    print("→ Valide visuellement AVANT de committer.")


if __name__ == "__main__":
    main("--write" in sys.argv)
