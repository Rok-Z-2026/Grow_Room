#!/usr/bin/env python3
"""
trim_fragments.py — retire les fragments parasites collés au bord HAUT d'un sprite
(= bout de la case voisine de l'atlas laissé par un mauvais détourage), puis re-rogne.

Sûr : ne retire qu'une composante connexe qui (a) touche la 1re/2e ligne de pixels,
(b) fait < 3% de la surface du sprite principal. Le contenu légitime (toit, cheminée,
pieds de château d'eau en bas) est connecté au corps ou trop gros → jamais touché.
Les sprites NATURE (feuillage légitimement fragmenté) sont exclus par défaut.

Usage :
  python3 tools/trim_fragments.py            # dry-run : liste ce qui serait retiré
  python3 tools/trim_fragments.py --write      # applique aux props
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

RUNTIME = Path(__file__).resolve().parent.parent / "02_Asset" / "runtime"
NATURE_PREFIX = ("plant_", "tree", "treeC", "bush", "bushF", "flower")


def is_nature(k):
    return any(k.startswith(p) for p in NATURE_PREFIX)


def clean_top_frags(im, max_frac=0.03):
    arr = np.asarray(im.convert("RGBA")).copy()
    a = arr[:, :, 3]
    mask = a > 40
    lbl, n = ndimage.label(mask, structure=np.ones((3, 3), int))
    if n <= 1:
        return im, 0
    sizes = ndimage.sum(np.ones_like(a), lbl, range(1, n + 1))
    mainsz = sizes.max()
    removed = 0
    for i in range(1, n + 1):
        if sizes[i - 1] >= max_frac * mainsz:
            continue
        ys, _ = np.where(lbl == i)
        if ys.min() <= 1:                 # collé au bord haut
            arr[lbl == i, 3] = 0
            removed += int(sizes[i - 1])
    if removed:
        a2 = arr[:, :, 3]
        ys, xs = np.where(a2 > 0)
        if len(ys):
            arr = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(arr), removed


def main(argv):
    write = "--write" in argv
    keys = sorted(p.stem for p in RUNTIME.glob("*.png") if not is_nature(p.stem))
    total = 0
    for k in keys:
        p = RUNTIME / (k + ".png")
        fixed, rm = clean_top_frags(Image.open(p))
        if rm:
            total += rm
            print("  %-13s -%d px%s" % (k, rm, "" if write else "  (dry-run)"))
            if write:
                fixed.save(p, "PNG", optimize=True)
    print("\nTotal retiré : %d px sur %d props%s" % (total, len(keys),
          "" if write else " — DRY-RUN"))
    if write:
        print("→ Régénère manifest si besoin (clés inchangées) et valide en jeu.")


if __name__ == "__main__":
    main(sys.argv)
