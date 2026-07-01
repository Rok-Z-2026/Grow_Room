#!/usr/bin/env python3
"""
extract_plantes.py — (re)génère les 48 sprites de plantes depuis Glow_Plante.png
vers 02_Asset/runtime/plant_<lettre>_<stade>.png  (archi externalisée).

Atlas Glow_Plante.png : grille 8 col × 6 lignes, cellule 384×435.
6 variétés = blocs 2×4 (stades 1-4 en haut, 5-8 en bas). Mapping atlas→moteur :
  v←V6 (vert)  p←V4 (violet)  b←V3 (bleu)  o←V2 (orange)  n←V1 (noir)  a←V5 (automne)

⚠️ Le CÂBLAGE MOTEUR (tableau ['v','p','b','o','n','a'], couleurs de burst, 6 boutons
   seedbar, boucle 4-plantes/case) est DÉJÀ appliqué dans le HTML live — ce script ne
   touche QUE les PNG runtime (re-skin). Voir tools/PROGRESS.md pour l'historique.

Usage :
  python3 tools/extract_plantes.py            # dry-run : preview des dimensions
  python3 tools/extract_plantes.py --write     # écrit les PNG runtime + enregistre les clés
"""
import sys
from PIL import Image
import asset_lib as A

COLS, ROWS = 8, 6
# variété (lettre) -> bloc (block_row, block_col) dans la grille de 6 blocs 2×4
VMAP = {"v": (2, 1), "p": (1, 1), "b": (1, 0), "o": (0, 1), "n": (0, 0), "a": (2, 0)}


def cell_box(cw, ch, br, bc, stage):
    lr = (stage - 1) // 4          # ligne locale 0/1
    lc = (stage - 1) % 4           # colonne locale 0..3
    r, c = br * 2 + lr, bc * 4 + lc
    return (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)


def main(write):
    atlas = Image.open(A.ASSET / "Glow_Plante.png").convert("RGBA")
    W, H = atlas.size
    cw, ch = W // COLS, H // ROWS
    print("Atlas %dx%d, cellule %dx%d" % (W, H, cw, ch))

    html = A.HTML.read_text(encoding="utf-8") if write else None
    added_total = []
    for letter, (br, bc) in VMAP.items():
        for st in range(1, 9):
            key = "plant_%s_%d" % (letter, st)
            spr = A.extract_sprite(atlas, cell_box(cw, ch, br, bc, st), keep_ratio=0.08)
            if spr is None:
                print("  !! VIDE", key); sys.exit(1)
            print("  %-12s %dx%d%s" % (key, spr.width, spr.height, "" if write else "  (dry-run)"))
            if write:
                html, added = A.register_key(html, key, spr)
                if added:
                    added_total.append(key)

    if not write:
        print("\nDry-run — rien écrit. Relance avec --write pour appliquer.")
        return
    A.HTML.write_text(html, encoding="utf-8")
    A.rebuild_manifest()
    print("\n48 PNG écrits. Nouvelles clés PACK :", added_total or "(aucune, re-skin pur)")
    print("Audit :", A.audit())
    print("→ Valide visuellement (Playwright 393×844 DPR2) AVANT de committer.")


if __name__ == "__main__":
    main("--write" in sys.argv)
