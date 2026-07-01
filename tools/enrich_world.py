#!/usr/bin/env python3
# Passe d'enrichissement : place les sprites premium SOUS-UTILISES (deja dans le
# PACK) pour sublimer la map. Ne touche PAS au PACK ni au moteur, seulement
# WORLD.decor. Toutes les poses sur cases VIDES + ground approprie, anti-overlap.
import json
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
h=open(HTML,encoding="utf-8").read()
i=h.find('WORLD='); j=h.find('};',i); seg=h[i+6:j+1]; W=json.loads(seg)
MW,MH=W['MW'],W['MH']; g=W['ground']; d=W['decor']; hg=W['hgt']; rp=W['ramps']

def empty(x,y): return 0<=x<MW and 0<=y<MH and d[y][x] is None and not rp[y][x]
def occupied_big(x,y,rad=1):
    BIG=('house1','house2','house3','house4','house5','cabin','atelier1','forge',
         'watertower','serre1','serre2','serre3','serre4','fountain','well','pond_big','pond_mare','cascade')
    for dy in range(-rad,rad+1):
        for dx in range(-rad,rad+1):
            nx,ny=x+dx,y+dy
            if 0<=nx<MW and 0<=ny<MH and d[ny][nx] and d[ny][nx][0] in BIG: return True
    return False

water=set((x,y) for y in range(MH) for x in range(MW) if g[y][x]=='water')
counts={}
def put(x,y,spr):
    d[y][x]=[spr,1]; counts[spr]=counts.get(spr,0)+1

# --- A. Berges fleuries : bushF/flower/bush alternes sur les cases vides au bord de l'eau
bank=[]
for (x,y) in water:
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
        nx,ny=x+dx,y+dy
        if empty(nx,ny) and g[ny][nx] in('grass','moss','sand') and (nx,ny) not in water:
            bank.append((nx,ny))
bank=sorted(set(bank))
for idx,(x,y) in enumerate(bank):
    if not empty(x,y): continue
    pick=['bushF','flower','bush','bushF','flower'][idx%5]
    var=(idx%6)+1
    put(x,y,pick if False else pick)  # placeholder; set with variant below
    d[y][x]=[pick,var]
counts['bank(bushF/flower/bush)']=len(bank)

# --- B. (cascade retiree : peu visible sur eau plate, n'ajoutait pas de valeur)

# --- C. Mares (pond_mare) dans des clairieres forestieres INTERIEURES (pres d'arbres)
def far_from(pts,x,y,dmin):
    return all(abs(px-x)+abs(py-y)>=dmin for px,py in pts)
def trees_around(x,y,rad=2):
    n=0
    for dy in range(-rad,rad+1):
        for dx in range(-rad,rad+1):
            nx,ny=x+dx,y+dy
            if 0<=nx<MW and 0<=ny<MH and d[ny][nx] and d[ny][nx][0] in('tree','treeC'): n+=1
    return n
clearings=[]
vil_center=(18,11)
for y in range(6,MH-6):
    for x in range(6,MW-6):
        if not empty(x,y): continue
        if g[y][x]!='grass' or hg[y][x]!=0: continue
        if (x,y) in water: continue
        if min((abs(wx-x)+abs(wy-y)) for wx,wy in water)<4: continue  # pas trop pres riviere
        if abs(x-vil_center[0])+abs(y-vil_center[1])<8: continue       # pas au village
        if occupied_big(x,y,2): continue
        if trees_around(x,y)<3: continue   # vraie clairiere boisee
        clearings.append((x,y))
# trie pour favoriser les clairieres bien boisees, puis disperse
clearings.sort(key=lambda p:-trees_around(*p))
placed_ponds=[]
for (x,y) in clearings:
    if len(placed_ponds)>=3: break
    if not far_from(placed_ponds,x,y,14): continue
    if occupied_big(x,y,2): continue
    put(x,y,'pond_mare'); placed_ponds.append((x,y))

# --- D. Village : fontaine + serres + atelier sur cases vides espacees, anti-overlap
def find_empty_spaced(cands,spr,n,spacing,placed):
    out=[]
    for (x,y) in cands:
        if len(out)>=n: break
        if not empty(x,y): continue
        if occupied_big(x,y,1): continue
        if not far_from(placed+out,x,y,spacing): continue
        put(x,y,spr); out.append((x,y))
    return out
vil_cells=[(x,y) for y in range(7,16) for x in range(12,25)
           if empty(x,y) and g[y][x] in('pavel','dirt')]
allplaced=[(18,11)]
allplaced+=find_empty_spaced(sorted(vil_cells,key=lambda p:abs(p[0]-18)+abs(p[1]-11)),'fountain',1,2,allplaced)
allplaced+=find_empty_spaced(vil_cells,'serre2',1,3,allplaced)
allplaced+=find_empty_spaced(vil_cells,'serre3',1,3,allplaced)
allplaced+=find_empty_spaced(vil_cells,'atelier1',1,3,allplaced)

# --- E. Cloture + panneau autour du champ possede (zone 18,38 n=3 -> cellules 18-20 x 38-40)
z=next(z for z in W['cropzones'] if z.get('owned'))
zx,zy,n=z['zx'],z['zy'],z['n']
# cases bordant la zone (anneau exterieur), vides, sol non-eau
ring=[]
for x in range(zx-1,zx+n+1):
    for y in range(zy-1,zy+n+1):
        if zx<=x<zx+n and zy<=y<zy+n: continue   # interieur = champ
        if empty(x,y) and (x,y) not in water and g[y][x]!='water':
            ring.append((x,y))
ring=sorted(set(ring))
# panneau a un coin, cloture bois sur quelques cases du pourtour
if ring:
    d[ring[0][1]][ring[0][0]]=['fence4',1]; counts['fence4']=1   # panneau
    fc=0
    for (x,y) in ring[1:]:
        if fc>=6: break
        if empty(x,y):
            var=[1,2,1,3,1,2][fc]   # melange bois/portail/muret
            d[y][x]=['fence'+str(var),var]; fc+=1
    counts['fence(bois/portail/muret)']=fc

W['decor']=d
newseg=json.dumps(W,separators=(', ',': '))
h2=h[:i+6]+newseg+h[j+1:]
# securite : nombre de data:image inchange (on ne touche pas le PACK)
assert h2.count('data:image')==h.count('data:image'),'PACK modifie -> abort'
open(HTML,"w",encoding="utf-8").write(h2)
print("ENRICH OK -> grow_world.html (NON commite)")
for k,v in counts.items(): print(f"  {k}: {v}")
print("  ponds:",placed_ponds)
print("  village add:",allplaced[1:])
