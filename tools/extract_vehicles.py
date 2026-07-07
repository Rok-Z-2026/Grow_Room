#!/usr/bin/env python3
"""
extract_vehicles.py — M3 « Le Chemin des Livraisons ».

Transforme les 47 sources `02_Asset/Transport_<N>_{Bas_G|Haut_D|Haut_D_&_Bas_G}.png`
(1024², RGBA à fond transparent) en sprites runtime `veh_<N>_{sw|ne}`.

- sw = Bas_G  (le véhicule descend vers le bas-gauche, il ARRIVE vers le joueur)
- ne = Haut_D (il monte vers le haut-droite, il REPART)
- N=1..22 : deux fichiers séparés -> deux clés.
- N=23..25 : un seul fichier combiné -> réutilisé pour les deux sens (convois symétriques).

Trim au bounding-box alpha (pas de chroma-key : fond déjà transparent) + downscale
(max côté = MAXDIM) pour garder des blobs légers (les sources 1024² sont bien trop
grandes pour ~1 tuile à l'écran). AUCUN redimensionnement in-game : decScale/decYOff
côté moteur calent la taille finale.
"""
import sys
from PIL import Image
import asset_lib as A

MAXDIM = 460   # côté max du sprite runtime (semis ~460 large ; largement net à DPR2)

def trimmed(path):
    im = Image.open(path).convert("RGBA")
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    s = MAXDIM / max(im.width, im.height)
    if s < 1:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return im

def main():
    html = A.HTML.read_text(encoding="utf-8")
    added, missing = [], []
    for n in range(1, 26):
        combo = A.ASSET / ("Transport_%d_Haut_D_&_Bas_G.png" % n)
        if combo.exists():                       # 23..25 : un sprite pour les 2 sens
            spr = trimmed(combo)
            for d in ("sw", "ne"):
                html, ok = A.register_key(html, "veh_%d_%s" % (n, d), spr)
                if ok: added.append("veh_%d_%s" % (n, d))
            continue
        for d, suffix in (("sw", "Bas_G"), ("ne", "Haut_D")):
            src = A.ASSET / ("Transport_%d_%s.png" % (n, suffix))
            if not src.exists():
                missing.append(src.name); continue
            html, ok = A.register_key(html, "veh_%d_%s" % (n, d), trimmed(src))
            if ok: added.append("veh_%d_%s" % (n, d))
    A.HTML.write_text(html, encoding="utf-8")
    keys = A.rebuild_manifest()
    rep = A.audit()
    print("ajoutées:", len(added), "| manquantes:", missing or "aucune")
    print("audit:", {k: rep[k] for k in ("png_files", "pack_keys", "manifest_keys")})
    print("pack_sans_png:", rep["pack_sans_png"] or "aucun")
    veh = sorted(k for k in keys if k.startswith("veh_"))
    print("clés veh_ (%d):" % len(veh), veh[:6], "...", veh[-3:])

if __name__ == "__main__":
    main()
