import sys
from playwright.sync_api import sync_playwright

S="/tmp/claude-0/-home-user-Grow-Room/6ca61300-ab28-5caa-8eb4-f03709beac01/scratchpad"
html=open(S+"/grow_world_new.html","r",encoding="utf-8").read()

# hook de test : debloque toutes les zones, plante 1 sprite/variete a divers stades,
# recadre la camera + zoom sur les plants. (uniquement dans la copie de test)
HOOK=r"""
<script>
(function(){
  function go(){
    if(typeof rebuildCrop!=='function'){return setTimeout(go,80);}
    var zs=(typeof W!=='undefined'&&W.cropzones)?W.cropzones:WORLD.cropzones;
    for(var i=0;i<zs.length;i++) zs[i].owned=true;
    rebuildCrop();
    // remplit la 1ere parcelle possedee -> bloc de cases pour juger le centrage
    var z0=null; for(var i=0;i<zs.length;i++){ if(zs[i].owned){ z0=zs[i]; break; } }
    var cbar=0,rbar=0,nn2=0,vi=0;
    for(var dy=0; dy<z0.n; dy++) for(var dx=0; dx<z0.n; dx++){
      var k=(z0.zx+dx)+','+(z0.zy+dy); var c=cropCells[k]; if(!c) continue;
      c.variety=vi%6; vi++; c.state='ready'; c.grow=1;
      cbar+=c.x; rbar+=c.y; nn2++;
    }
    if(nn2>0){ cbar/=nn2; rbar/=nn2;
      try{ zoom=1.15;
        cam.x=-(cbar-rbar)*TW()/2;
        cam.y=APP_H*0.5-APP_H*0.28-(cbar+rbar)*TH()/2;
        clampCam();
      }catch(e){}
    }
    window.__ready=true;
  }
  go();
})();
</script>
"""
html=html.replace("</body>", HOOK+"\n</body>", 1)
open(S+"/grow_world_test.html","w",encoding="utf-8").write(html)
print("grow_world_test.html ecrit")

with sync_playwright() as p:
    try:
        browser=p.chromium.launch()
    except Exception as e:
        print("launch defaut KO, executable_path:",e)
        browser=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    ctx=browser.new_context(viewport={"width":393,"height":844},device_scale_factor=2,
                            is_mobile=True,has_touch=True)
    page=ctx.new_page()
    errs=[]
    page.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None)
    page.on("pageerror",lambda e: errs.append("PAGEERROR: "+str(e)))
    page.goto("file://"+S+"/grow_world_test.html")
    page.wait_for_timeout(6500)   # laisse charger les 170 images + setup + rAF
    page.screenshot(path=S+"/shot_plants.png")
    print("screenshot -> shot_plants.png")
    print("__ready =", page.evaluate("window.__ready||false"))
    if errs: print("CONSOLE:\n"+"\n".join(errs[:15]))
    else: print("aucune erreur console")
    browser.close()
