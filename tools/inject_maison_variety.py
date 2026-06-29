#!/usr/bin/env python3
"""
inject_maison_variety.py

Detoure ~8 batiments INEXPLOITES de l'atlas Glow_Maison.png (suppression de la
tuile de sol losange en herbe, on garde le batiment + petite base) et les injecte
dans le PACK base64 de grow_world.html sous de NOUVELLES cles (regle d'or #2 :
insertion apres `const PACK={` SANS effacer les autres cles).

Atlas: 2560x2048, grille 5col x 4lignes, cellule 512x512.

Mapping cle moteur <- cellule atlas:
  house5   <- R1C0 (maison 2 etages toit ardoise sombre)
  house6   <- R2C1 (chaumiere tuiles brunes + veranda)
  house7   <- R0C4 (chaumiere toit ardoise bleu)
  house8   <- R1C1 (chaumiere toit mousse/fleurs, porte arrondie)
  house9   <- R0C3 (ferme toit de chaume + roue de chariot)
  serre5   <- R2C2 (grande serre verre)
  etal1    <- R1C3 (etal de marche, store raye, cagettes)
  atelier2 <- R3C0 (abri ouvert en bois, toit mousse)

Comme les batiments occupent quasi toute la largeur de cellule, on garde une bande
centrale large (`foliage_half` ~ 240) au-dessus du plan de sol, et une base large
(`motte_half`) sous le plan, le tout en retirant l'herbe par couleur.

Usage:
  python3 inject_maison_variety.py            # detour + QA pngs + injection PACK
  python3 inject_maison_variety.py --detour-only
"""
import re, sys, os, io, base64
import numpy as np
from PIL import Image

ATLAS = "/home/user/Grow_Room/02_Asset/Glow_Maison.png"
HTML  = "/home/user/Grow_Room/01_Code/grow_world.html"
OUT   = "/tmp/claude-0/-home-user-Grow-Room/6a94929b-4c52-52be-9494-012322a2a21e/scratchpad"

CW, CH = 512, 512

# key, (row,col), params
#  foliage_half : demi-largeur conservee AU-DESSUS du plan de sol (= la structure).
#                 Les batiments sont larges -> ~240 (presque toute la cellule).
#  motte_half   : demi-largeur de la base conservee SOUS le plan de sol.
#  motte_depth  : profondeur (px) de base gardee sous le plan du sol.
#  extra_lift   : remonte du sommet du losange si besoin.
JOBS = [
    ("house5",   (1, 0), dict(foliage_half=244, motte_half=170, motte_depth=20)),
    ("house6",   (2, 1), dict(foliage_half=244, motte_half=170, motte_depth=20)),
    ("house7",   (0, 4), dict(foliage_half=244, motte_half=160, motte_depth=20)),
    ("house8",   (1, 1), dict(foliage_half=244, motte_half=170, motte_depth=20)),
    ("house9",   (0, 3), dict(foliage_half=244, motte_half=170, motte_depth=20)),
    ("serre5",   (2, 2), dict(foliage_half=244, motte_half=180, motte_depth=20)),
    ("etal1",    (1, 3), dict(foliage_half=244, motte_half=190, motte_depth=22)),
    ("atelier2", (3, 0), dict(foliage_half=244, motte_half=185, motte_depth=22)),
]


def _ground_top(m, y_bottom):
    """Sommet du losange de sol par symetrie autour de sa rangee la plus large
    (cherchee dans la moitie basse de la cellule)."""
    widths = m.sum(axis=1)
    lo = CH // 2
    y_wide = lo + int(np.argmax(widths[lo:]))
    half_h = y_bottom - y_wide
    y_top = y_wide - half_h
    return max(0, int(y_top)), int(y_wide), int(widths[y_wide])


def detour_cell(atlas, row, col, foliage_half=244, motte_half=170,
                motte_depth=20, extra_lift=0):
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
    y_ground = y_wide

    xx = np.arange(CW)
    R, G, B = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    # herbe verte (la tuile de sol) -> SOL a virer. Les feuillages/lierres muraux
    # sont au-dessus du plan de sol et restent dans la bande large quoi qu'il arrive,
    # donc on n'applique le filtre couleur que pour la zone basse (motte) et au plan.
    grass = (G > R + 8) & (G > B + 2) & (G > 55) & (R < 170)

    # halos noirs / speckles AA des bords
    dark = (R < 28) & (G < 28) & (B < 28)
    blackhalo = dark & (alpha > 16) & (alpha < 230)

    y_cut = y_ground + motte_depth
    new_m = m.copy()
    for y in range(0, CH):
        if y < y_top:
            continue  # garde tout le haut tel quel
        if y >= y_cut:
            new_m[y] = False
            continue
        if y < y_ground:
            # zone structure : bande large, on retire l'herbe (bordure de tuile qui
            # depasse parfois sur les cotes) mais on garde le bati.
            band = np.abs(xx - cx) < foliage_half
            new_m[y] = m[y] & band & (~grass[y])
        else:
            # zone base : bande etroite + retrait herbe
            band = np.abs(xx - cx) < motte_half
            new_m[y] = m[y] & band & (~grass[y])

    new_m = new_m & (~blackhalo)

    out = arr.copy()
    out[:, :, 3] = np.where(new_m, alpha, 0).astype(np.uint8)

    nys, nxs = np.where(new_m)
    if len(nys) == 0:
        return Image.fromarray(out, "RGBA"), {}
    x0, x1 = int(nxs.min()), int(nxs.max()) + 1
    y0, y1 = int(nys.min()), int(nys.max()) + 1
    trimmed = Image.fromarray(out[y0:y1, x0:x1], "RGBA")
    dbg = dict(y_bottom=y_bottom, y_wide=y_wide, GW=GW, y_top=y_top,
               fol=foliage_half, motte=motte_half, size=trimmed.size)
    return trimmed, dbg


def png_datauri(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    raw = buf.getvalue()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def main():
    detour_only = "--detour-only" in sys.argv
    atlas = Image.open(ATLAS).convert("RGBA")

    results = []
    for key, (r, c), params in JOBS:
        img, dbg = detour_cell(atlas, r, c, **params)
        p = os.path.join(OUT, "maison_%s.png" % key)
        img.save(p)
        results.append((key, img, dbg, p))
        print("DETOUR %-9s R%dC%d -> %s  %s" % (key, r, c, dbg.get("size"), dbg))

    if detour_only:
        return

    html = open(HTML, "r", encoding="utf-8", errors="replace").read()
    before = html.count("data:image")

    # Guard regle d'or #2 : aucune des nouvelles cles ne doit deja exister
    for key, *_ in results:
        assert ('"%s"' % key) not in html, "cle %s existe deja !" % key

    # Construire le bloc d'insertion
    inject = ""
    for key, img, dbg, p in results:
        uri, nbytes = png_datauri(img)
        inject += '"%s":"%s",' % (key, uri)
        print("PACK   %-9s -> %d bytes png" % (key, nbytes))

    anchor = "const PACK={"
    idx = html.find(anchor)
    assert idx != -1, "ancre PACK introuvable"
    pos = idx + len(anchor)
    html = html[:pos] + inject + html[pos:]

    after = html.count("data:image")
    assert after == before + len(results), \
        "count data:image attendu %d, obtenu %d" % (before + len(results), after)
    print("data:image count: before=%d after=%d (+%d) OK" % (before, after, len(results)))

    open(HTML, "w", encoding="utf-8").write(html)
    print("WROTE", HTML)


if __name__ == "__main__":
    main()
