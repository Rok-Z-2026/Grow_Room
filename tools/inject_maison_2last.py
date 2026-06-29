#!/usr/bin/env python3
# Integre les 2 DERNIERS batiments inexploites de Glow_Maison -> 20/20.
#   house10 <- R1C2 ; house11 <- R1C4
# Reutilise le detourage de inject_maison_variety.py. decScale/isBig couvrent
# deja house* via startsWith('house'). Injecte les cles + place dans le village.
import sys, os, io, base64, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from PIL import Image
from inject_maison_variety import detour_cell, png_datauri, ATLAS, HTML, OUT

JOBS = [
    ("house10", (1, 2), dict(foliage_half=244, motte_half=170, motte_depth=20)),
    ("house11", (1, 4), dict(foliage_half=244, motte_half=170, motte_depth=20)),
]

def main():
    detour_only = "--detour-only" in sys.argv
    atlas = Image.open(ATLAS).convert("RGBA")
    results = []
    for key, (r, c), params in JOBS:
        img, dbg = detour_cell(atlas, r, c, **params)
        p = os.path.join(OUT, "maison_%s.png" % key); img.save(p)
        results.append((key, img)); print("DETOUR %-8s R%dC%d -> %s" % (key, r, c, dbg.get("size")), "->", p)
    if detour_only:
        return

    html = open(HTML, encoding="utf-8", errors="replace").read()
    before = html.count("data:image")
    for key, _ in results:
        assert ('"%s"' % key) not in html, "cle %s existe deja" % key
    inject = "".join('"%s":"%s",' % (key, png_datauri(img)[0]) for key, img in results)
    anchor = "const PACK={"; pos = html.find(anchor) + len(anchor)
    html = html[:pos] + inject + html[pos:]
    after = html.count("data:image")
    assert after == before + len(results), "count %d->%d" % (before, after)

    # placement dans le village (cases vides grass/pavel, hors cropzones, anti-overlap)
    i = html.find("WORLD="); j = html.find("};", i); W = json.loads(html[i+6:j+1])
    MW, MH = W["MW"], W["MH"]; dec = W["decor"]; gnd = W["ground"]
    zone = set()
    for z in W["cropzones"]:
        for dy in range(z["n"]):
            for dx in range(z["n"]):
                zone.add((z["zx"]+dx, z["zy"]+dy))
    BIG = {"tree","treeC","cabin","etal1","atelier1","atelier2","pond_big","pond_mare","cascade"}
    def big_near(x, y):
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<MW and 0<=ny<MH:
                    d=dec[ny][nx]
                    if d and (d[0] in BIG or d[0].startswith("house") or d[0].startswith("serre")): return True
        return False
    placed = []
    cands = [(x,y) for y in range(7,17) for x in range(12,28)
             if dec[y][x] is None and gnd[y][x] in ("grass","pavel") and (x,y) not in zone]
    for (x,y) in cands:
        if len(placed) >= len(results): break
        if big_near(x,y): continue
        if any(abs(px-x)+abs(py-y) < 3 for px,py in placed): continue
        dec[y][x] = [results[len(placed)][0], 1]; placed.append((x,y))
    assert len(placed) == len(results), "placement incomplet: %s" % placed
    W["decor"] = dec
    html = html[:i+6] + json.dumps(W, separators=(", ", ": ")) + html[j+1:]

    open(HTML, "w", encoding="utf-8").write(html)
    print("data:image %d -> %d (+%d) | places: %s" % (before, after, len(results),
          list(zip([k for k,_ in results], placed))))

if __name__ == "__main__":
    main()
