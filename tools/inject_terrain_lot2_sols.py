import re, base64, io, sys
import numpy as np
from PIL import Image
from scipy import ndimage

S="/tmp/claude-0/-home-user-Grow-Room/6ca61300-ab28-5caa-8eb4-f03709beac01/scratchpad"
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
atlas=Image.open(S+"/Glow_Terrain.png").convert("RGBA"); G=512

# sq_key -> (row,col) cellule sol de l'atlas
MAP={
 "sq_grass":(5,7),  # gazon vert + fleurs
 "sq_moss":(7,6),   # herbe/mousse verte
 "sq_dirt":(7,1),   # terre brun-sombre
 "sq_gravel":(7,4), # gravier brun
 "sq_mud":(6,3),    # terre labouree/boue
 "sq_path":(7,3),   # dalle/pierre fissuree
 "sq_sand":(7,2),   # sable ocre
 "sq_soil":(7,5),   # terre jaune-ocre
 "sq_stone":(5,5),  # pave gris
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
print("sols extraits :")
for k,(r,c) in MAP.items():
    sp=extract(r,c)
    if sp is None: print("VIDE",k); sys.exit(1)
    buf=io.BytesIO(); sp.save(buf,"PNG",optimize=True)
    new[k]="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
    print(f"  {k:9s} R{r}C{c}  {sp.width}x{sp.height}")

html=open(HTML,encoding="utf-8").read()
before=html.count('data:image')
pat=re.compile(r'"(sq_grass|sq_moss|sq_dirt|sq_gravel|sq_mud|sq_path|sq_sand|sq_soil|sq_stone)"\s*:\s*"data:image[^"]*"')
seen=set()
def repl(m):
    k=m.group(1)
    if k in new: seen.add(k); return '"%s":"%s"'%(k,new[k])
    return m.group(0)
html=pat.sub(repl,html)
print("\nremplaces:",len(seen),"/",len(MAP))
if set(MAP)-seen: print("MANQUE:",set(MAP)-seen); sys.exit(1)
after=html.count('data:image')
assert after==before,"compte change -> abort"
open(HTML,"w",encoding="utf-8").write(html)
print("OK -> grow_world.html mis a jour (NON commite). data-uris:",after)
