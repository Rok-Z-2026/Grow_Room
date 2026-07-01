#!/usr/bin/env python3
# Purge des assets HORS-ATLAS pour une map 100% issue des 5 atlas.
#  - retire du monde les placements de : house5, well, fountain, forge, watertower
#  - supprime ces 5 cles du PACK + les 7 textures d'eau MORTES (water1-6, waterTex)
#    (confirmees 0 reference dans le code moteur)
# Les literaux 'well'/'forge'/... restant dans decScale/isBig sont inoffensifs
# (simples chaines de comparaison, jamais atteintes sans decor correspondant).
import re, json
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
h=open(HTML,encoding="utf-8").read()
before=h.count('data:image')

BUILDINGS={'house5','well','fountain','forge','watertower'}
DEAD_WATER={'water1','water2','water3','water4','water5','water6','waterTex'}

# 1) retirer les placements dans WORLD.decor
i=h.find('WORLD='); j=h.find('};',i); W=json.loads(h[i+6:j+1])
MW,MH=W['MW'],W['MH']; d=W['decor']; removed={}
for y in range(MH):
    for x in range(MW):
        c=d[y][x]
        if c and c[0] in BUILDINGS:
            removed[c[0]]=removed.get(c[0],0)+1; d[y][x]=None
W['decor']=d
h=h[:i+6]+json.dumps(W,separators=(', ',': '))+h[j+1:]
print("placements retires:",removed)

# 2) supprimer les cles du PACK (aucune n'est la 1ere cle -> virgule precedente sure)
purged=[]
for k in sorted(BUILDINGS|DEAD_WATER):
    pat=re.compile(r',\s*"'+re.escape(k)+r'"\s*:\s*"data:image[^"]*"')
    h,n=pat.subn('',h)
    assert n==1, "cle %s supprimee %d fois (attendu 1)"%(k,n)
    purged.append(k)
after=h.count('data:image')
assert after==before-len(purged), "compte data:image %d->%d (attendu -%d)"%(before,after,len(purged))
open(HTML,"w",encoding="utf-8").write(h)
print("cles purgees (%d):"%len(purged),purged)
print("data:image %d -> %d"%(before,after))
