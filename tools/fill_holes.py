#!/usr/bin/env python3
"""
fill_holes.py — bouche les TROUS enclavés (pixels transparents parasites) dans les
PNG runtime, sans toucher aux grandes zones transparentes voulues (verre des serres).

Cause du bug : d'anciennes extractions (composantes connexes + seuil alpha) ont percé
des trous à l'intérieur des sprites (surtout les bâtiments) → on voit le fond à travers.

Méthode : pour chaque trou enclavé (région transparente NON connectée au bord) de surface
<= max_hole px, on le remplit avec la couleur opaque la plus proche et alpha=255.
Les grandes zones (verre, arches ouvertes) dépassent le seuil → intactes.

Usage :
  python3 tools/fill_holes.py                 # dry-run : rapport des trous par clé
  python3 tools/fill_holes.py --write          # applique aux clés STRUCTURES
  python3 tools/fill_holes.py --write k1 k2     # applique à des clés précises
  python3 tools/fill_holes.py --max-hole 120    # ajuste le seuil de taille
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

RUNTIME = Path(__file__).resolve().parent.parent / "02_Asset" / "runtime"

# Bâtiments / structures / props man-made (la "ville")
STRUCTURES = [
    "house1", "house2", "house3", "house4", "house5",
    "serre1", "serre2", "serre3", "serre4",
    "cabin", "atelier1", "watertower", "forge", "well", "fountain", "cuve", "arch",
    "bench", "lamp", "cart", "barrel", "crate", "compost", "planter",
    "fence1", "fence2", "fence3", "fence4",
]


def fill_small_holes(im, max_hole=80):
    """Retourne (image_corrigée, nb_px_bouchés). Ne remplit que les trous <= max_hole."""
    arr = np.asarray(im.convert("RGBA")).copy()
    a = arr[:, :, 3]
    opaque = a > 32
    transp = ~opaque
    lbl, n = ndimage.label(transp)
    if n == 0:
        return Image.fromarray(arr), 0
    border = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]])))
    sizes = ndimage.sum(np.ones_like(a), lbl, range(1, n + 1))
    tofill = np.zeros_like(opaque)
    for i in range(1, n + 1):
        if i in border:
            continue
        if sizes[i - 1] <= max_hole:
            tofill |= (lbl == i)
    nfill = int(tofill.sum())
    if nfill:
        inds = ndimage.distance_transform_edt(~opaque, return_distances=False, return_indices=True)
        for ch in range(3):
            src = arr[:, :, ch][tuple(inds)]
            arr[:, :, ch][tofill] = src[tofill]
        arr[:, :, 3][tofill] = 255
    return Image.fromarray(arr), nfill


def main(argv):
    write = "--write" in argv
    max_hole = 80
    if "--max-hole" in argv:
        max_hole = int(argv[argv.index("--max-hole") + 1])
    keys = [a for a in argv[1:] if not a.startswith("--") and a != str(max_hole)] or STRUCTURES

    total = 0
    for k in keys:
        p = RUNTIME / (k + ".png")
        if not p.exists():
            print("  (absent)", k); continue
        im = Image.open(p)
        fixed, nf = fill_small_holes(im, max_hole)
        total += nf
        print("  %-11s %+d px%s" % (k, nf, "" if write else "  (dry-run)"))
        if write and nf:
            fixed.save(p, "PNG", optimize=True)

    print("\nTotal px bouchés : %d sur %d clés (seuil %dpx)%s" % (
        total, len(keys), max_hole, "" if write else " — DRY-RUN, rien écrit"))
    if write:
        print("→ Valide visuellement (screenshot in-game) AVANT de committer.")


if __name__ == "__main__":
    main(sys.argv)
