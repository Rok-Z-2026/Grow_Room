#!/usr/bin/env python3
# Lot 4 — Champignons. Extrait les amanites (Glow_Terrain R2C6), ajoute la cle
# PACK "mushroom", cable decScale, et disperse des champignons sur le sol
# forestier (cases herbe/mousse vides proches d'un arbre).
import re, base64, io, json
import numpy as np
from PIL import Image
from scipy import ndimage

S="/tmp/claude-0/-home-user-Grow-Room/6a94929b-4c52-52be-9494-012322a2a21e/scratchpad"
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
atlas=Image.open(S+"/Glow_Terrain.png").convert("RGBA"); G=512

def extract(r,c,keep=0.05):
    cell=np.array(atlas.crop((c*G,r*G,c*G+G,r*G+G)))
    m=cell[:,:,3]>16
    lbl,n=ndimage.label(m,structure=np.ones((3,3),int))
    sz=ndimage.sum(np.ones_like(m),lbl,range(1,n+1)); mx=sz.max()
    km=np.isin(lbl,[i+1 for i,s in enumerate(sz) if s>=keep*mx]); cell[~km,3]=0
    ys,xs=np.where(km)
    return Image.fromarray(cell).crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))

sp=extract(2,6)
buf=io.BytesIO(); sp.save(buf,"PNG",optimize=True)
uri="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
print("mushroom sprite",sp.size)

html=open(HTML,encoding="utf-8").read()
before=html.count('data:image')

# 1) injecter la cle PACK juste apres "const PACK={" (regle d'or #2 : ne rien effacer)
assert '"mushroom":' not in html, "mushroom deja present -> abort"
anchor='const PACK={'
i=html.index(anchor)+len(anchor)
html=html[:i]+'"mushroom":"%s",'%uri+html[i:]

# 2) decScale : champignons petits
old='function decScale(t){'
assert html.count(old)==1
html=html.replace(old, old+"if(t==='mushroom')return 0.62;",1)

# 3) placement dans WORLD : dispersion sur sol forestier
mi=html.find('WORLD='); mj=html.find('};',mi)
seg=html[mi+6:mj+1]; W=json.loads(seg)
MW,MH=W['MW'],W['MH']; dec=W['decor']; gnd=W['ground']; hgt=W['hgt']; ramps=W['ramps']

def near_tree(x,y):
    for dy in(-1,0,1):
        for dx in(-1,0,1):
            nx,ny=x+dx,y+dy
            if 0<=nx<MW and 0<=ny<MH:
                d=dec[ny][nx]
                if d and d[0] in('tree','treeC'): return True
    return False

placed=0
# scatter deterministe (hash) -> reproductible, pas de RNG
for y in range(MH):
    for x in range(MW):
        if dec[y][x] is not None: continue
        if ramps[y][x]: continue
        if gnd[y][x] not in('grass','moss'): continue
        if hgt[y][x]>1: continue
        if not near_tree(x,y): continue
        # densite ~1/6 des cases eligibles, motif pseudo-aleatoire stable
        if ((x*73856093) ^ (y*19349663)) % 6 != 0: continue
        dec[y][x]=['mushroom',1]; placed+=1

print("champignons places:",placed)
W['decor']=dec
newseg=json.dumps(W,separators=(', ',': '))
html=html[:mi+6]+newseg+html[mj+1:]

after=html.count('data:image')
assert after==before+1, "compte data:image inattendu: %d -> %d"%(before,after)
open(HTML,"w",encoding="utf-8").write(html)
print("OK -> grow_world.html (NON commite). data-uris:",after)
