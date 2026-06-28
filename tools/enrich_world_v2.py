#!/usr/bin/env python3
# Passe d'enrichissement v2 — map verdoyante & enchanteresque.
# S'applique PAR-DESSUS l'etat courant (mushrooms + enrich v1 deja commis).
# Ne touche ni au PACK ni au moteur : seulement WORLD.ground et WORLD.decor.
#  1) verdissement : terre/sable -> herbe (garde les allees pavel + l'eau)
#  2) accents de mousse sur le sol forestier
#  3) prairie de fleurs sauvages + buissons fleuris
#  4) plus de champignons pres des arbres
#  5) etangs a nenuphars (pond_big) dans des clairieres OUVERTES (visibles)
#  6) cloture + panneau autour des champs achetables
import json
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
h=open(HTML,encoding="utf-8").read()
i=h.find('WORLD='); j=h.find('};',i); W=json.loads(h[i+6:j+1])
MW,MH=W['MW'],W['MH']; g=W['ground']; d=W['decor']; hg=W['hgt']; rp=W['ramps']

# empreinte de toutes les zones de culture (on n'y pose jamais de decor)
zone_cells=set()
for z in W['cropzones']:
    for dy in range(z['n']):
        for dx in range(z['n']):
            zone_cells.add((z['zx']+dx, z['zy']+dy))

def H(x,y): return 0<=x<MW and 0<=y<MH
def empty(x,y):
    return H(x,y) and d[y][x] is None and not rp[y][x] and (x,y) not in zone_cells and g[y][x]!='water'
def hsh(x,y,salt=0):
    return ((x*73856093) ^ (y*19349663) ^ (salt*83492791)) & 0x7fffffff
def ntype(x,y,types,rad=1):
    n=0
    for dy in range(-rad,rad+1):
        for dx in range(-rad,rad+1):
            if H(x+dx,y+dy) and d[y+dy][x+dx] and d[y+dy][x+dx][0] in types: n+=1
    return n
counts={}
def inc(k,n=1): counts[k]=counts.get(k,0)+n

water=set((x,y) for y in range(MH) for x in range(MW) if g[y][x]=='water')

# 1) VERDISSEMENT terre/sable -> herbe (les chemins pavel restent)
greened=0
for y in range(MH):
    for x in range(MW):
        if g[y][x] in('dirt','sand'):
            g[y][x]='grass'; greened+=1
inc('verdi(dirt/sand->grass)',greened)

# 1b) DE-PAVAGE : le pave forme un grand reseau de rayures (effet dallage) sur tout
#     le champ. On ne garde qu'une place compacte au village ; le reste -> herbe.
VBX0,VBX1,VBY0,VBY1=12,24,6,15   # boite du village (batiments x13-23,y8-14)
depave=0
for y in range(MH):
    for x in range(MW):
        if g[y][x]=='pavel' and not(VBX0<=x<=VBX1 and VBY0<=y<=VBY1):
            g[y][x]='grass'; depave+=1
inc('depave(pavel->grass)',depave)

# 2) ACCENTS DE MOUSSE sur sol forestier (sous les arbres)
mossed=0
for y in range(MH):
    for x in range(MW):
        if g[y][x]=='grass' and ntype(x,y,('tree','treeC'),1)>=2 and hsh(x,y,1)%2==0:
            g[y][x]='moss'; mossed+=1
inc('mousse(grass->moss forest)',mossed)

# 3) PRAIRIE FLEURIE : fleurs sauvages + buissons fleuris sur herbe/mousse vide
fl=bf=0
for y in range(MH):
    for x in range(MW):
        if not empty(x,y): continue
        if g[y][x] not in('grass','moss'): continue
        rh=hsh(x,y,2)
        if rh%8==0:                      # ~1/8 -> fleurs
            d[y][x]=['flower',(rh//8)%6+1]; fl+=1
        elif rh%17==0:                   # ~1/17 -> buisson fleuri
            d[y][x]=['bushF',(rh//17)%6+1]; bf+=1
inc('fleurs',fl); inc('buissons_fleuris',bf)

# 4) PLUS DE CHAMPIGNONS pres des arbres (s'ajoute aux 53 existants)
mu=0
for y in range(MH):
    for x in range(MW):
        if not empty(x,y): continue
        if g[y][x] not in('grass','moss') or hg[y][x]>1: continue
        if ntype(x,y,('tree','treeC'),1)>=1 and hsh(x,y,3)%5==0:
            d[y][x]=['mushroom',1]; mu+=1
inc('champignons_ajoutes',mu)

# 5) ETANGS A NENUPHARS (pond_big) dans des clairieres OUVERTES et visibles
def far(pts,x,y,dmin): return all(abs(px-x)+abs(py-y)>=dmin for px,py in pts)
cand=[]
for y in range(6,MH-6):
    for x in range(6,MW-6):
        if not empty(x,y) or g[y][x]!='grass' or hg[y][x]!=0: continue
        if (x,y) in zone_cells: continue
        if water and min(abs(wx-x)+abs(wy-y) for wx,wy in water)<5: continue
        if abs(x-18)+abs(y-11)<7: continue          # pas dans le village
        if ntype(x,y,('tree','treeC'),2)>0: continue # OUVERT (aucun arbre a rad2 -> visible)
        if ntype(x,y,('house1','house2','house3','house4','house5','cabin','atelier1',
                      'forge','watertower','serre1','serre2','serre3','serre4','fountain',
                      'well','pond_big','pond_mare'),2)>0: continue
        cand.append((x,y))
ponds=[]
for (x,y) in cand:
    if len(ponds)>=3: break
    if not far(ponds,x,y,16): continue
    # nettoie un petit halo autour pour bien le mettre en valeur
    d[y][x]=['pond_big',1]; ponds.append((x,y))
inc('etangs_nenuphars',len(ponds))

# 6) CLOTURE + PANNEAU autour des champs achetables (non possedes)
fence_total=0; signs=0
for z in W['cropzones']:
    if z.get('owned'): continue
    zx,zy,n=z['zx'],z['zy'],z['n']
    ring=[]
    for x in range(zx-1,zx+n+1):
        for y in range(zy-1,zy+n+1):
            if zx<=x<zx+n and zy<=y<zy+n: continue
            if empty(x,y): ring.append((x,y))
    ring=sorted(set(ring))
    if not ring: continue
    sx,sy=ring[0]; d[sy][sx]=['fence4',1]; signs+=1
    fc=0
    for (x,y) in ring[1:]:
        if fc>=5: break
        if empty(x,y):
            var=[1,2,1,3,2][fc]; d[y][x]=['fence'+str(var),var]; fc+=1
    fence_total+=fc
inc('panneaux',signs); inc('cloture_segments',fence_total)

W['ground']=g; W['decor']=d
newseg=json.dumps(W,separators=(', ',': '))
h2=h[:i+6]+newseg+h[j+1:]
assert h2.count('data:image')==h.count('data:image'),'PACK modifie -> abort'
open(HTML,"w",encoding="utf-8").write(h2)
print("ENRICH v2 OK (NON commite)")
for k,v in counts.items(): print(f"  {k}: {v}")
print("  ponds:",ponds)
