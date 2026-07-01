#!/usr/bin/env python3
"""
extract_terrain_sols.py — (re)génère les sols sq_* depuis Glow_Terrain.png vers
02_Asset/runtime/sq_*.png.

Atlas Glow_Terrain.png : grille 8×8, cellule 512×512.
⚠️ Les cellules de sol sont des tuiles iso (≈70% transparent) ; le moteur les clippe
   au losange dans tile() (ow = w*1.12). Les sols couvrent TOUTE la carte →
   VALIDER VISUELLEMENT avant de committer (règle d'or #4).

Usage :
  python3 tools/extract_terrain_sols.py           # dry-run
  python3 tools/extract_terrain_sols.py --write     # écrit les PNG runtime + clés
"""
import sys
from PIL import Image
import asset_lib as A

G = 512
MAP = {
    "sq_grass": (5, 7),   # gazon vert + fleurs
    "sq_moss": (7, 6),    # herbe/mousse verte
    "sq_dirt": (7, 1),    # terre brun-sombre
    "sq_gravel": (7, 4),  # gravier brun
    "sq_mud": (6, 3),     # terre labourée/boue
    "sq_path": (7, 3),    # dalle/pierre fissurée
    "sq_sand": (7, 2),    # sable ocre
    "sq_soil": (7, 5),    # terre jaune-ocre
    "sq_stone": (5, 5),   # pavé gris
}


def main(write):
    atlas = Image.open(A.ASSET / "Glow_Terrain.png").convert("RGBA")
    html = A.HTML.read_text(encoding="utf-8") if write else None
    added_total = []
    for key, (r, c) in MAP.items():
        spr = A.extract_sprite(atlas, (c * G, r * G, c * G + G, r * G + G), keep_ratio=0.05)
        if spr is None:
            print("  !! VIDE", key); sys.exit(1)
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
    print("\nSols écrits. Nouvelles clés PACK :", added_total or "(aucune, re-skin pur)")
    print("Audit :", A.audit())
    print("→ Sols = toute la carte : VALIDE VISUELLEMENT avant de committer.")


if __name__ == "__main__":
    main("--write" in sys.argv)
