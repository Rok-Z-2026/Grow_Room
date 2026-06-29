#!/usr/bin/env python3
# Purge des assets DORMANTS non-atlas (0 placement, 0 lecture d'image moteur).
# Idempotent (ignore une cle deja absente).
#  - 14 props non-atlas : barrel, bench, lamp, cuve, crate, cart, planter,
#    potplant, potflower, compost, arch, paved, field_wet, field_border
#  - 8 textures de sol PRE-ATLAS (remplacees par les sols atlas sq_*) :
#    grass, dirt, sand, soil, moss, mud, gravel, pavel
#    (les litteraux 'grass'/'dirt'... de groundKey() restent : ce sont des
#     chaines de comparaison, pas des lectures d'image — groundKey -> sq_*).
# Conserve les tuiles fonctionnelles (parc1-4, ramp_*, wallTex, sq_*).
import re, json
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
PROPS=['barrel','bench','lamp','cuve','crate','cart','planter','potplant',
       'potflower','compost','arch','paved','field_wet','field_border']
GROUNDS=['grass','dirt','sand','soil','moss','mud','gravel','pavel']
KEYS=PROPS+GROUNDS

h=open(HTML,encoding="utf-8").read()
before=h.count('data:image')
i=h.find('WORLD='); j=h.find('};',i); W=json.loads(h[i+6:j+1])
placed=set(c[0] for row in W['decor'] for c in row if c)
purged=[]
for k in KEYS:
    assert k not in placed, "ABORT: %s est placee dans le monde"%k
    pat=re.compile(r',\s*"'+re.escape(k)+r'"\s*:\s*"data:image[^"]*"')
    h,n=pat.subn('',h)
    assert n<=1, "cle %s : %d matchs"%(k,n)
    if n==1: purged.append(k)
after=h.count('data:image')
# garde-fou : sols atlas + groundKey intacts
for k in GROUNDS:
    assert k=='pavel' or ('"sq_'+k+'"' in h), "sq_"+k+" disparu !"
assert "function groundKey" in h
open(HTML,"w",encoding="utf-8").write(h)
print("purgees (%d):"%len(purged),purged)
print("data:image %d -> %d"%(before,after))
