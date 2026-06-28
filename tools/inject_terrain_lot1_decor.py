import re, base64, io, sys
import numpy as np
from PIL import Image
from scipy import ndimage

S="/tmp/claude-0/-home-user-Grow-Room/6ca61300-ab28-5caa-8eb4-f03709beac01/scratchpad"
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
atlas=Image.open(S+"/Glow_Terrain.png").convert("RGBA")
G=512

MAP={
 "bush1":(0,0),"bush2":(0,3),"bush3":(0,4),"bush4":(0,6),"bush5":(1,2),"bush6":(0,1),
 "bushF1":(0,2),"bushF2":(0,5),"bushF3":(1,0),"bushF4":(1,1),"bushF5":(1,3),"bushF6":(0,7),
 "flower1":(4,5),"flower2":(4,6),"flower3":(4,7),"flower4":(5,0),"flower5":(5,1),"flower6":(5,2),
 "rock1":(1,4),"rock2":(1,5),"rock3":(1,6),"rock4":(1,7),"rock5":(2,0),"rock6":(2,1),
 "stump1":(2,2),"stump2":(2,3),"stump3":(4,2),"stump4":(2,4),"stump5":(2,7),"stump6":(4,3),
}
def extract(r,c):
    cell=np.array(atlas.crop((c*G,r*G,c*G+G,r*G+G)))
    m=cell[:,:,3]>16
    if m.sum()==0: return None
    lbl,n=ndimage.label(m,structure=np.ones((3,3),int))
    sz=ndimage.sum(np.ones_like(m),lbl,range(1,n+1)); mx=sz.max()
    keep=[i+1 for i,s in enumerate(sz) if s>=0.05*mx]
    km=np.isin(lbl,keep); cell[~km,3]=0
    ys,xs=np.where(km)
    return Image.fromarray(cell).crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))

new={}
print("sanity (cle : taille trimmee) :")
for k,(r,c) in MAP.items():
    sp=extract(r,c)
    if sp is None: print("  !! VIDE",k,(r,c)); sys.exit(1)
    buf=io.BytesIO(); sp.save(buf,"PNG",optimize=True)
    new[k]="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
    print(f"  {k:8s} R{r}C{c}  {sp.width}x{sp.height}")

html=open(HTML,encoding="utf-8").read()
before=html.count('data:image')
pat=re.compile(r'"(bush[1-6]|bushF[1-6]|flower[1-6]|rock[1-6]|stump[1-6])"\s*:\s*"data:image[^"]*"')
seen=set()
def repl(m):
    k=m.group(1)
    if k in new: seen.add(k); return '"%s":"%s"'%(k,new[k])
    return m.group(0)
html=pat.sub(repl,html)
print("\ncles remplacees:",len(seen),"/ 30")
missing=set(MAP)-seen
if missing: print("!! MANQUANTES dans le PACK:",missing); sys.exit(1)
after=html.count('data:image')
assert after==before, "compte data-uris change (%d->%d) -> abort"%(before,after)
open(HTML,"w",encoding="utf-8").write(html)
print("OK -> grow_world.html mis a jour (data-uris inchanges:",after,")")
