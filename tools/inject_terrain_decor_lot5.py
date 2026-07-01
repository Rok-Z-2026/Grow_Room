#!/usr/bin/env python3
"""
TINY GROW — Integration deco terrain inexploitee (Lot 5).
Detoure 4 cases de Glow_Terrain.png (retire la tuile sol losange herbe, garde la
deco + petite base) et AJOUTE de nouvelles cles PACK (sans rien effacer, regle d'or #2).
Cles: leaves1 (R4C0), bundle1 (R4C1), moundflora1 (R3C7), rockpile1 (R3C0).
Usage: python3 tools/inject_terrain_decor_lot5.py [--dry]
"""
import re, base64, io, sys, os
from PIL import Image
import numpy as np

ROOT="/home/user/Grow_Room"
ATLAS=os.path.join(ROOT,"02_Asset","Glow_Terrain.png")
HTML=os.path.join(ROOT,"01_Code","grow_world.html")
SCRATCH="/tmp/claude-0/-home-user-Grow-Room/6a94929b-4c52-52be-9494-012322a2a21e/scratchpad"
C=512

# cle -> (row,col, keep_half, top_lift, base_keep)
# deco au sol : peu de hauteur, on garde une large base (keep_half grand) car
# la deco occupe presque toute la largeur de la tuile (pas un tronc fin).
MAP={
 "leaves1":     dict(rc=(4,0), keep_half=150, top_lift=8,  base_keep=120), # feuilles automne (tapis large)
 "bundle1":     dict(rc=(4,1), keep_half=170, top_lift=6,  base_keep=130), # fagots/rondins (large, bas)
 "moundflora1": dict(rc=(3,7), keep_half=170, top_lift=10, base_keep=150), # monticule fleuri (volumineux)
 "rockpile1":   dict(rc=(3,0), keep_half=160, top_lift=10, base_keep=140), # amas rochers
}

def detour(cell, keep_half, top_lift, base_keep):
    a=np.array(cell).astype(np.int16)
    m=a[:,:,3]>16
    ys,xs=np.where(m)
    y_bottom=ys.max()
    cx=C//2
    widths=np.zeros(C,dtype=int)
    for y in range(C):
        r=np.where(m[y])[0]
        if len(r): widths[y]=r.max()-r.min()
    lower=widths.copy(); lower[:C//2]=0
    wy=int(np.argmax(lower)); GW=int(widths[wy])
    # tuile losange 2:1 : sommet = wy - GW/4
    y_top=int(wy-GW/4)-top_lift
    y_top=max(0,y_top)
    newm=m.copy()
    yy=np.arange(C)[:,None]; xx=np.arange(C)[None,:]
    y_cut=y_top+base_keep
    frac=np.clip((yy-y_top)/max(1,base_keep),0,1)
    half_at_y=keep_half*(1.0-0.45*frac)   # se resserre vers le bas
    in_band=(yy>y_top)&(yy<=y_cut)
    central=(np.abs(xx-cx)<half_at_y)
    newm[in_band&(~central)]=False
    newm[np.broadcast_to(yy>y_cut,(C,C))]=False
    out=a.copy(); out[~newm,3]=0; out=out.astype(np.uint8)
    img=Image.fromarray(out,"RGBA")
    bbox=img.getbbox(); img=img.crop(bbox)
    return img, dict(y_bottom=y_bottom,GW=GW,y_top=y_top,size=img.size)

def png_bytes(img):
    b=io.BytesIO(); img.save(b,"PNG",optimize=True); return b.getvalue()

def main():
    dry="--dry" in sys.argv
    atlas=Image.open(ATLAS).convert("RGBA")
    html=open(HTML,encoding="utf-8",errors="replace").read()
    before=html.count("data:image")
    new_uris={}; results={}
    for key,cfg in MAP.items():
        r,c=cfg["rc"]
        cell=atlas.crop((c*C,r*C,c*C+C,r*C+C))
        img,info=detour(cell,cfg["keep_half"],cfg["top_lift"],cfg["base_keep"])
        raw=png_bytes(img)
        out=os.path.join(SCRATCH,"new_%s.png"%key); img.save(out)
        new_uris[key]="data:image/png;base64,"+base64.b64encode(raw).decode()
        results[key]=dict(info=info,png=out,bytes=len(raw),rc=(r,c))
        print("%-12s r%dc%d size=%s y_top=%d GW=%d png=%dKB -> %s"%(
            key,r,c,img.size,info["y_top"],info["GW"],len(raw)//1024,out))
    if dry:
        print("DRY: pas d'ecriture."); return results
    # garde-fou: ne pas re-ajouter si deja present
    for key in new_uris:
        if re.search(r'"'+re.escape(key)+r'"\s*:\s*"data:image',html):
            raise SystemExit("cle %s deja presente — abort"%key)
    # injection apres const PACK={  (regle d'or #2)
    anchor="const PACK={"
    idx=html.find(anchor)
    assert idx>=0, "const PACK={ introuvable"
    ins=idx+len(anchor)
    block="".join('"%s":"%s",'%(k,u) for k,u in new_uris.items())
    html=html[:ins]+block+html[ins:]
    after=html.count("data:image")
    assert after==before+len(new_uris), "count attendu %d, obtenu %d"%(before+len(new_uris),after)
    open(HTML,"w",encoding="utf-8").write(html)
    print("data:image: %d -> %d (+%d) OK"%(before,after,len(new_uris)))
    return results

if __name__=="__main__":
    main()
