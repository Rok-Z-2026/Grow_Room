import re, base64, io, sys
import numpy as np
from PIL import Image
from scipy import ndimage

S="/tmp/claude-0/-home-user-Grow-Room/6ca61300-ab28-5caa-8eb4-f03709beac01/scratchpad"
atlas=Image.open(S+"/Glow_Plante.png").convert("RGBA")
W,H=atlas.size
COLS,ROWS=8,6
cw,ch=W//COLS,H//ROWS   # 384 x 435

# variete (lettre) -> bloc (block_row, block_col).  6 blocs 2x4.
# v<-V6, p<-V4, b<-V3, o<-V2, n<-V1, a<-V5
VMAP={'v':(2,1),'p':(1,1),'b':(1,0),'o':(0,1),'n':(0,0),'a':(2,0)}

def cell_sprite(br,bc,stage):
    # stage 1..8 -> local_row 0/1, local_col 0..3
    lr=(stage-1)//4; lc=(stage-1)%4
    r=br*2+lr; c=bc*4+lc
    box=(c*cw, r*ch, (c+1)*cw, (r+1)*ch)
    cell=np.array(atlas.crop(box))   # copie editable
    mask=(cell[:,:,3]>16)
    # composantes connexes 2D (8-connexite) : la plante+sol = 1 grosse masse,
    # les intrusions des cellules voisines (haut/bas/gauche/droite) = petits blobs detaches
    lbl,n=ndimage.label(mask, structure=np.ones((3,3),int))
    if n==0: return None,None
    sizes=ndimage.sum(np.ones_like(mask),lbl,range(1,n+1))
    mx=sizes.max()
    keep=[i+1 for i,s in enumerate(sizes) if s>=0.08*mx]   # garde la masse principale (et tout blob >=8%)
    keepmask=np.isin(lbl,keep)
    cell[~keepmask,3]=0                                     # efface les fragments
    ys,xs=np.where(keepmask)
    bb=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)
    return Image.fromarray(cell).crop(bb), bb

new={}; dims={}
for letter,(br,bc) in VMAP.items():
    for st in range(1,9):
        spr,bb=cell_sprite(br,bc,st)
        buf=io.BytesIO(); spr.save(buf,"PNG",optimize=True)
        uri="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()
        key="plant_%s_%d"%(letter,st)
        new[key]=uri; dims[key]=spr.size
print("sprites extraits:",len(new))
print("exemples dims (l x h) :",{k:dims[k] for k in ['plant_v_1','plant_v_8','plant_n_8','plant_a_8','plant_o_4']})

# --- charge le HTML ---
html=open(S+"/grow_world.html","r",encoding="utf-8",errors="replace").read()
before=html.count('data:image')
print("\nPACK avant: %d data-uris"%before)

def must(old, label):
    n=html.count(old)
    if n!=1:
        print("!! ABORT: '%s' trouve %d fois (attendu 1)"%(label,n)); sys.exit(1)

# 1) PACK : remplacer en place les 32 cles existantes plant_[vpbo]_[1-8]
pat=re.compile(r'"(plant_[vpbo]_[1-8])"\s*:\s*"data:image[^"]*"')
seen=set()
def repl(m):
    k=m.group(1); seen.add(k); return '"%s":"%s"'%(k,new[k])
html=pat.sub(repl,html)
print("cles existantes re-skinnees:",len(seen),"(attendu 32)")
assert len(seen)==32,"re-skin incomplet"

# 2) PACK : prepend des 16 nouvelles cles (n,a) apres 'const PACK={'  (regle d'or #2)
inject="".join('"%s":"%s",'%(k,new[k]) for k in new if k[6] in "na")
must("const PACK={","ancre const PACK={")
html=html.replace("const PACK={","const PACK={"+inject,1)

after=html.count('data:image')
print("PACK apres: %d data-uris (attendu %d)"%(after,before+16))
assert after==before+16,"compte de cles incoherent -> on n'ecrit pas"

# 3) Moteur : index->lettre (4 -> 6 varietes)
old_arr="['v','p','b','o'][c.variety]"; must(old_arr,"array varietes")
html=html.replace(old_arr,"['v','p','b','o','n','a'][c.variety]",1)

# 4) Moteur : couleurs de burst (ajout noir + automne)
old_col="['#8bd450','#b86bff','#5a9bff','#ff9d3c'][c.variety]"; must(old_col,"array couleurs")
html=html.replace(old_col,"['#8bd450','#b86bff','#5a9bff','#ff9d3c','#9b8fb5','#e0913c'][c.variety]",1)

# 5) Moteur : 4 plantes/case RECENTREES sur la case
#    (sprites a sol integre -> on resserre les positions et on reduit le decalage avant
#     pour que le buisson tombe au centre du losange, pas vers l'avant)
old_loop=("for(const[fc,fr]of[[0.38,0.38],[0.62,0.38],[0.38,0.62],[0.62,0.62]])"
          "{const sx=isoX(x+fc,y+fr),sy=isoY(x+fc,y+fr)+TH()*0.42;"
          "drawSp(IMG['plant_'+v+'_'+st],sx,sy,TW()*(0.22+0.18*(st/8)));}")
must(old_loop,"boucle 4 plantes")
new_loop=("for(const[fc,fr]of[[0.30,0.30],[0.70,0.30],[0.30,0.70],[0.70,0.70]])"
          "{const sx=isoX(x+fc,y+fr),sy=isoY(x+fc,y+fr)+TH()*0.12;"
          "drawSp(IMG['plant_'+v+'_'+st],sx,sy,TW()*(0.28+0.20*(st/8)));}")
html=html.replace(old_loop,new_loop,1)

# 6) HTML seedbar : +2 boutons (Noire, Automne)
orange='<button class="seed" data-v="3"><span class="ico">🍊</span><span class="nm">Orange</span></button>'
must(orange,"bouton orange")
extra=(orange+
       '\n    <button class="seed" data-v="4"><span class="ico">🖤</span><span class="nm">Noire</span></button>'
       '\n    <button class="seed" data-v="5"><span class="ico">🍁</span><span class="nm">Automne</span></button>')
html=html.replace(orange,extra,1)

# 7) CSS : flex-wrap pour 6 boutons sur mobile
old_css=".seeds{display:flex;gap:10px;justify-content:center;}"; must(old_css,"css .seeds")
html=html.replace(old_css,".seeds{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;}",1)

open(S+"/grow_world_new.html","w",encoding="utf-8").write(html)
print("\nOK -> grow_world_new.html ecrit (%d chars)"%len(html))

# verif : toutes les 48 cles plant presentes
keys=set(re.findall(r'"(plant_[a-z]_[1-8])"\s*:\s*"data:image',html))
print("cles plant_ presentes:",len(keys),"(attendu 48)")
assert len(keys)==48
