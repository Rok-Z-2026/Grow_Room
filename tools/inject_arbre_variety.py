#!/usr/bin/env python3
"""
inject_arbre_variety.py

Detoure 6 arbres de l'atlas Glow_Arbre.png (suppression de la tuile de sol losange
en herbe, on garde l'arbre + petite motte centrale) et les injecte chirurgicalement
dans le PACK base64 de grow_world.html.

Mapping clé moteur <- cellule atlas (grille 4col x 3lignes, cellule 512x600):
  tree4  <- R0C2 (bouleau tronc epais)
  treeC1 <- R1C3 (bouleau elance 2 troncs)
  treeC2 <- R1C2 (chene noueux variante)
  treeC3 <- R1C1 (gros pommier charge)
  treeC4 <- R2C0 (saule + etang -> on garde l'arbre, on enleve l'etang/sol)
  treeC5 <- R2C3 (sapin elance)

Regle d'or #2: on remplace UNIQUEMENT la data-uri de ces 6 cles, jamais les autres.

Usage:
  python3 inject_arbre_variety.py            # detour + QA pngs + injection
  python3 inject_arbre_variety.py --detour-only
"""
import re, sys, os, io, base64
import numpy as np
from PIL import Image

ATLAS = "/home/user/Grow_Room/02_Asset/Glow_Arbre.png"
HTML  = "/home/user/Grow_Room/01_Code/grow_world.html"
OUT   = "/tmp/claude-0/-home-user-Grow-Room/6a94929b-4c52-52be-9494-012322a2a21e/scratchpad"

CW, CH = 512, 600

# key, (row,col), per-tree params overriding defaults
# trunk_half : demi-largeur de la colonne centrale conservee sous y_top (tronc + motte)
# extra_lift : remonte (px) supplementaire du y_top (sol) pour les arbres dont le
#              feuillage/branches descendent (saule pendant) -> on coupe plus haut
#              pour ne pas garder de l'herbe, MAIS on remet le feuillage via keep_leaf.
# keep_leaf  : sous y_top, en plus du tronc, garder les pixels NON-verts (feuillage
#              pendant brun/clair) -> evite de rogner les branches du saule.
JOBS = [
    ("tree4",  (0, 2), dict(trunk_half=40, motte_half=40, motte_depth=18)),  # bouleau tronc epais
    ("treeC1", (1, 3), dict(trunk_half=58, motte_half=52, motte_depth=18)),  # bouleau elance 2 troncs
    ("treeC2", (1, 2), dict(trunk_half=58, motte_depth=22)),              # chene noueux
    ("treeC3", (1, 1), dict(trunk_half=58, motte_depth=22)),              # gros pommier
    ("treeC4", (2, 0), dict(trunk_half=70, foliage_half=150, motte_half=58, motte_depth=24)),  # saule pendant
    ("treeC5", (2, 3), dict(trunk_half=50, motte_depth=18)),              # sapin elance
]


def _ground_top(m, y_bottom):
    """Detecte le sommet du losange de sol par symetrie autour de sa rangee la
    plus large (cherchee dans la moitie basse de la cellule)."""
    widths = m.sum(axis=1)
    lo = CH // 2
    y_wide = lo + int(np.argmax(widths[lo:]))      # rangee la plus large du bas
    half_h = y_bottom - y_wide                       # demi-hauteur du losange
    y_top = y_wide - half_h                           # sommet du losange (symetrie)
    return max(0, int(y_top)), int(y_wide), int(widths[y_wide])


def detour_cell(atlas, row, col, trunk_half=50, extra_lift=0,
                foliage_half=0, motte_half=None, motte_depth=42):
    """Detoure une cellule. Deux zones sous le sommet du losange:

      zone FEUILLAGE  [y_top .. y_ground] : garde une bande large `foliage_half`
          (utile pour les branches pendantes du saule), sol retire par couleur.
      zone MOTTE      [y_ground .. bas]   : garde seulement `motte_half` (tronc +
          petite motte), sol (herbe/eau) retire par couleur.

    `foliage_half`=0 -> on utilise trunk_half partout (arbres a couronne haute).
    """
    crop = atlas.crop((col * CW, row * CH, col * CW + CW, row * CH + CH)).convert("RGBA")
    arr = np.array(crop)
    alpha = arr[:, :, 3]
    m = alpha > 16
    ys, xs = np.where(m)
    if len(ys) == 0:
        return crop, {}
    y_bottom = int(ys.max())
    cx = CW // 2  # 256

    y_top, y_wide, GW = _ground_top(m, y_bottom)
    y_top = max(0, y_top - extra_lift)
    y_ground = y_wide  # plan du sol (rangee la plus large du losange)

    if foliage_half <= 0:
        foliage_half = trunk_half
    if motte_half is None:
        motte_half = trunk_half

    xx = np.arange(CW)
    # classer les pixels: herbe (vert sature) et eau (etang emeraude) = SOL a virer.
    R, G, B = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    grass = (G > R + 8) & (G > B + 2) & (G > 55) & (R < 170)
    # eau de l'etang: teinte bleu/cyan sombre OU bleu clair, peu de rouge
    water = (B > R + 10) & (G > R) & (B > 70)
    soil = grass | water

    # halos noirs / speckles d'anti-aliasing de l'atlas (bords sombres semi-opaques)
    dark = (R < 28) & (G < 28) & (B < 28)
    blackhalo = dark & (alpha > 16) & (alpha < 230)

    y_cut = y_ground + motte_depth  # au-dela: plus rien (la motte est courte)
    new_m = m.copy()
    for y in range(y_top, CH):
        if y >= y_cut:
            new_m[y] = False
            continue
        if y < y_ground:
            band = np.abs(xx - cx) < foliage_half
        else:
            band = np.abs(xx - cx) < motte_half
        new_m[y] = m[y] & band & (~soil[y])

    # supprimer les halos noirs partout (foliage compris)
    new_m = new_m & (~blackhalo)

    out = arr.copy()
    out[:, :, 3] = np.where(new_m, alpha, 0).astype(np.uint8)

    # trim au bbox du nouveau masque
    nys, nxs = np.where(new_m)
    if len(nys) == 0:
        return Image.fromarray(out, "RGBA"), {}
    x0, x1 = int(nxs.min()), int(nxs.max()) + 1
    y0, y1 = int(nys.min()), int(nys.max()) + 1
    trimmed = Image.fromarray(out[y0:y1, x0:x1], "RGBA")
    dbg = dict(y_bottom=y_bottom, y_wide=y_wide, GW=GW, y_top=y_top,
               trunk_half=trunk_half, fol=foliage_half, motte=motte_half,
               size=trimmed.size)
    return trimmed, dbg


def png_datauri(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    raw = buf.getvalue()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def main():
    detour_only = "--detour-only" in sys.argv
    atlas = Image.open(ATLAS).convert("RGBA")

    results = {}
    for key, (r, c), params in JOBS:
        img, dbg = detour_cell(atlas, r, c, **params)
        p = os.path.join(OUT, "detour_%s.png" % key)
        img.save(p)
        results[key] = (img, dbg, p)
        print("DETOUR %-7s R%dC%d -> %s  %s" % (key, r, c, dbg.get("size"), dbg))

    if detour_only:
        return

    html = open(HTML, "r", encoding="utf-8", errors="replace").read()
    before = html.count("data:image")
    for key, (img, dbg, p) in results.items():
        uri, nbytes = png_datauri(img)
        pat = re.compile(r'("' + re.escape(key) + r'"\s*:\s*")data:image[^"]*(")')
        new_html, n = pat.subn(lambda mm: mm.group(1) + uri + mm.group(2), html, count=1)
        assert n == 1, "cle %s: %d remplacement(s) (attendu 1)" % (key, n)
        html = new_html
        print("INJECT %-7s -> %d bytes png" % (key, nbytes))
    after = html.count("data:image")
    assert before == after, "count data:image change! %d -> %d" % (before, after)
    print("data:image count: before=%d after=%d (OK)" % (before, after))

    open(HTML, "w", encoding="utf-8").write(html)
    print("WROTE", HTML)


if __name__ == "__main__":
    main()
