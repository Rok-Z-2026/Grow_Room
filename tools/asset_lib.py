#!/usr/bin/env python3
"""
asset_lib.py — Boîte à outils du pipeline d'assets TINY GROW (archi EXTERNALISÉE).

Depuis l'externalisation du PACK (~30 Mo base64 → 170 PNG dans 02_Asset/runtime/),
le workflow d'intégration d'un asset est :

    1. Découper le sprite depuis un atlas Glow_* (extract_sprite).
    2. L'écrire en PNG dans 02_Asset/runtime/<clé>.png    (save_runtime).
    3. Enregistrer la clé : tableau `const PACK=[...]` du HTML + manifest.json
       (register_key / rebuild_manifest).

⚠️ On NE ré-embarque JAMAIS de base64 dans le HTML (ça casserait tout le gain de poids).
⚠️ La clé DOIT matcher exactement le nom de fichier (casse sensible sous GitHub Pages).

Chemins déduits automatiquement depuis l'emplacement de ce fichier (racine du repo),
donc plus de chemins 'scratchpad' à rafistoler entre sessions.
"""
import io
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

# --- Chemins repo-relatifs (ce fichier vit dans tools/) --------------------
REPO = Path(__file__).resolve().parent.parent
HTML = REPO / "01_Code" / "grow_world.html"
ASSET = REPO / "02_Asset"
RUNTIME = ASSET / "runtime"
MANIFEST = RUNTIME / "manifest.json"


# --- Extraction ------------------------------------------------------------
def extract_sprite(atlas, box, keep_ratio=0.05):
    """Découpe la case `box`=(x0,y0,x1,y1) d'un atlas RGBA, retire les fragments
    des cases voisines (composantes connexes < keep_ratio du plus gros blob),
    puis rogne au bounding-box alpha. Retourne un PIL.Image RGBA (ou None si vide).

    C'est la logique éprouvée du pipeline (scipy.ndimage.label, 8-connexité)."""
    cell = np.array(atlas.crop(box))  # copie éditable
    mask = cell[:, :, 3] > 16
    if mask.sum() == 0:
        return None
    lbl, n = ndimage.label(mask, structure=np.ones((3, 3), int))
    sizes = ndimage.sum(np.ones_like(mask), lbl, range(1, n + 1))
    mx = sizes.max()
    keep = [i + 1 for i, s in enumerate(sizes) if s >= keep_ratio * mx]
    keepmask = np.isin(lbl, keep)
    cell[~keepmask, 3] = 0  # efface les fragments détachés
    ys, xs = np.where(keepmask)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    return Image.fromarray(cell).crop(bb)


# --- Écriture PNG runtime --------------------------------------------------
def save_runtime(key, image):
    """Écrit `image` en 02_Asset/runtime/<key>.png (PNG optimisé). Retourne le chemin."""
    RUNTIME.mkdir(parents=True, exist_ok=True)
    out = RUNTIME / (key + ".png")
    image.save(out, "PNG", optimize=True)
    return out


# --- Gestion du tableau PACK dans le HTML ----------------------------------
def _pack_span(html):
    """Retourne (start_bracket, end_bracket) du tableau `const PACK=[...]`."""
    i = html.find("const PACK=[")
    if i < 0:
        raise RuntimeError("ancre 'const PACK=[' introuvable — HTML au mauvais format ?")
    lb = html.index("[", i)
    depth, j, instr, esc = 0, lb, False, False
    while j < len(html):
        c = html[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return lb, j
        j += 1
    raise RuntimeError("tableau PACK non terminé")


def pack_keys(html=None):
    """Liste des clés déclarées dans le tableau `const PACK=[...]` du HTML."""
    if html is None:
        html = HTML.read_text(encoding="utf-8")
    lb, rb = _pack_span(html)
    return re.findall(r'"([^"]+)"', html[lb:rb + 1])


def add_keys_to_pack(html, keys):
    """Ajoute `keys` (absentes) dans le tableau `const PACK=[...]`. Idempotent.
    Retourne (nouveau_html, liste_ajoutées)."""
    lb, rb = _pack_span(html)
    existing = set(re.findall(r'"([^"]+)"', html[lb:rb + 1]))
    added = [k for k in keys if k not in existing]
    if not added:
        return html, []
    ins = "".join(',"%s"' % k for k in added)
    new = html[:rb] + ins + html[rb:]
    return new, added


# --- Manifest --------------------------------------------------------------
def rebuild_manifest():
    """Régénère manifest.json à partir des PNG présents dans runtime/ (triés).
    Retourne la liste des clés."""
    keys = sorted(p.stem for p in RUNTIME.glob("*.png"))
    MANIFEST.write_text(json.dumps(keys, ensure_ascii=False), encoding="utf-8")
    return keys


def register_key(html, key, image):
    """Raccourci : écrit le PNG runtime + ajoute la clé au tableau PACK.
    Retourne (nouveau_html, ajoutée?). N'écrit PAS le HTML sur disque (à toi de le faire)."""
    save_runtime(key, image)
    html, added = add_keys_to_pack(html, [key])
    return html, bool(added)


# --- Contrôle d'intégrité --------------------------------------------------
def audit():
    """Vérifie la cohérence PACK(tableau HTML) ⇄ manifest.json ⇄ fichiers PNG.
    Retourne un dict de rapport ; lève AssertionError si incohérence bloquante."""
    files = {p.stem for p in RUNTIME.glob("*.png")}
    pack = set(pack_keys())
    man = set(json.loads(MANIFEST.read_text(encoding="utf-8"))) if MANIFEST.exists() else set()
    rep = {
        "png_files": len(files),
        "pack_keys": len(pack),
        "manifest_keys": len(man),
        "pack_sans_png": sorted(pack - files),   # clé déclarée mais fichier absent → image cassée
        "png_sans_pack": sorted(files - pack),   # fichier présent mais jamais chargé
        "manifest_desync": sorted(man ^ files),  # manifest != fichiers réels
    }
    assert not rep["pack_sans_png"], "Clés PACK sans PNG (images cassées) : %s" % rep["pack_sans_png"]
    return rep


if __name__ == "__main__":
    from pprint import pprint
    print("Repo :", REPO)
    pprint(audit())
