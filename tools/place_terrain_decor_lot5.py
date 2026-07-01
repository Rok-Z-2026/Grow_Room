#!/usr/bin/env python3
"""
Placement WORLD.decor pour les 4 nouvelles deco (Lot 5).
- Cases VIDES (decor None) sur sol grass/moss, dans l'interieur (marge 4),
  hors cropzones (+marge), anti-overlap (pas adjacent a une grosse deco existante).
- Motif pseudo-aleatoire STABLE via hash(x,y,type).
Modifie WORLD={...} en place dans le HTML.
Usage: python3 tools/place_terrain_decor_lot5.py [--dry]
"""
import re, json, sys, hashlib, os

HTML="/home/user/Grow_Room/01_Code/grow_world.html"

def h(*a):
    s="|".join(map(str,a))
    return int(hashlib.md5(s.encode()).hexdigest()[:8],16)

BIG={'tree','treeC','house1','house2','house3','house4','house5','house6','house7',
     'house8','house9','serre1','serre2','serre3','serre5','cabin','atelier1','atelier2',
     'etal1','watertower','forge','pond_big','pond_mare','cascade'}

# type -> (cible nb placements max, ground prefere)
PLAN=[
 ("leaves1",     22, None),   # tapis de feuilles, partout en foret
 ("bundle1",     16, None),   # fagots, pres souches/arbres
 ("moundflora1", 12, None),   # monticule fleuri, clairieres
 ("rockpile1",   14, None),   # amas rochers, lisieres
]

def load():
    html=open(HTML,encoding="utf-8",errors="replace").read()
    s=html.find("WORLD={"); i=html.find("{",s); d=0
    for j in range(i,len(html)):
        if html[j]=='{':d+=1
        elif html[j]=='}':
            d-=1
            if d==0: end=j+1;break
    return html,i,end,json.loads(html[i:end])

def main():
    dry="--dry" in sys.argv
    html,i,end,W=load()
    MW,MH=W["MW"],W["MH"]
    dec=W["decor"]; ground=W["ground"]; hgt=W["hgt"]
    crop=W["cropzones"]
    # masque interdit autour des cropzones (n=span)
    blocked=set()
    for cz in crop:
        zx,zy,n=cz["zx"],cz["zy"],cz["n"]
        for yy in range(zy-1,zy+n+1):
            for xx in range(zx-1,zx+n+1):
                blocked.add((xx,yy))
    # adjacence grosse deco
    def near_big(x,y):
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<MW and 0<=ny<MH:
                    c=dec[ny][nx]
                    if c and c[0] in BIG: return True
        return False
    placed={t:0 for t,_,_ in PLAN}
    # parcours stable
    coords=[(x,y) for y in range(4,MH-4) for x in range(4,MW-4)]
    # ordonne par hash pour dispersion
    for t,target,_pref in PLAN:
        cnt=0
        # iterate coords sorted by per-type hash
        ordered=sorted(coords,key=lambda p:h(p[0],p[1],t))
        for (x,y) in ordered:
            if cnt>=target: break
            if dec[y][x] is not None: continue
            if (x,y) in blocked: continue
            g=ground[y][x]
            if g not in ("grass","moss"): continue
            if near_big(x,y): continue
            # densite : ~1 chance sur 2 selon hash, pour disperser
            if h(x,y,t,"d")%100 < 55:
                dec[y][x]=[t,0]
                cnt+=1
        placed[t]=cnt
    print("placements:",placed, "total",sum(placed.values()))
    if dry:
        print("DRY: pas d'ecriture.")
        return placed
    newjson=json.dumps(W,separators=(", ",": "))
    newhtml=html[:i]+newjson+html[end:]
    open(HTML,"w",encoding="utf-8").write(newhtml)
    print("WORLD reecrit. nouvelle decor non-null:",
          sum(1 for r in dec for c in r if c))
    return placed

if __name__=="__main__":
    main()
