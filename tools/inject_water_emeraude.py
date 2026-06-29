#!/usr/bin/env python3
# Eau émeraude conforme à l'atlas Grow_Water_1.png.
#  1) ré-injecte water_f0-3 depuis les 4 quadrants de l'atlas (place du placeholder cyan)
#  2) remplace le dégradé CYAN hardcodé du moteur par des tons ÉMERAUDE tirés de
#     l'atlas (règle d'or #3 : ne pas hardcoder une couleur a la place de l'atlas)
#  3) remonte un peu l'alpha des frames pour que la texture atlas domine
import re, base64, io
import numpy as np
from PIL import Image
S="/tmp/claude-0/-home-user-Grow-Room/6a94929b-4c52-52be-9494-012322a2a21e/scratchpad"
ATL="/home/user/Grow_Room/02_Asset/Grow_Water_1.png"
HTML="/home/user/Grow_Room/01_Code/grow_world.html"

a=Image.open(ATL).convert("RGBA"); W,Hh=a.size; qw,qh=W//2,Hh//2
# quadrants -> water_f0..f3 (ordre de lecture TL,TR,BL,BR), downscale 512 (taille fichier)
quads={
 'water_f0':(0,0), 'water_f1':(1,0), 'water_f2':(0,1), 'water_f3':(1,1),
}
new={}
arr=np.array(a)[:,:,:3].reshape(-1,3).mean(0)
print("atlas avgRGB ~",tuple(int(v) for v in arr))
for k,(cx,cy) in quads.items():
    q=a.crop((cx*qw,cy*qh,cx*qw+qw,cy*qh+qh)).resize((512,512),Image.LANCZOS).convert("RGB")
    buf=io.BytesIO(); q.save(buf,"PNG",optimize=True)
    new[k]="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
    print(f"  {k}: 512x512  {len(buf.getvalue())//1024} Ko")

h=open(HTML,encoding="utf-8").read()
before=h.count('data:image')
for k,uri in new.items():
    pat=re.compile('("'+k+'"\\s*:\\s*")data:image[^"]*(")')
    h,n=pat.subn(lambda m:m.group(1)+uri+m.group(2),h)
    assert n==1, "cle %s remplacee %d fois"%(k,n)
after=h.count('data:image')
assert after==before, "compte data:image change %d->%d"%(before,after)

# --- dégradé émeraude (depuis l'atlas, ~ (34,75,63)) : clair en surface -> profond ---
OLD_GRAD="grd.addColorStop(0,'#5fc4d6');grd.addColorStop(0.5,'#3a9cb8');grd.addColorStop(1,'#256b86');"
NEW_GRAD="grd.addColorStop(0,'#5cbf9e');grd.addColorStop(0.5,'#2f9678');grd.addColorStop(1,'#155446');"
assert h.count(OLD_GRAD)==1, "degrade cyan introuvable/non unique"
h=h.replace(OLD_GRAD,NEW_GRAD,1)

# --- alpha des frames : 0.78 -> 0.9 pour que la texture atlas domine le tint ---
assert h.count("ctx.globalAlpha=0.78;ctx.drawImage(f1")==1
h=h.replace("ctx.globalAlpha=0.78;ctx.drawImage(f1","ctx.globalAlpha=0.9;ctx.drawImage(f1",1)
assert h.count("ctx.globalAlpha=0.78*blend;ctx.drawImage(f2")==1
h=h.replace("ctx.globalAlpha=0.78*blend;ctx.drawImage(f2","ctx.globalAlpha=0.9*blend;ctx.drawImage(f2",1)

open(HTML,"w",encoding="utf-8").write(h)
print("OK -> eau emeraude injectee (NON commite). data:image:",after)
