#!/usr/bin/env python3
# TINY GROW — sondage santé end-to-end (Playwright).
# Boote le jeu réel servi en HTTP (assets + audio résolus), boot direct #nointro, attend les
# étapes lazy (eau vivante WATER_FR, audio SND.ctx), drive TOUTES les scènes (panneaux DOM),
# screenshote chacune, et capture les pageerror/console.error en continu.
#
# Usage : python3 tools/audit_health.py [--out DIR] [--keep]
# Sortie : rapport JSON sur stdout + captures dans DIR (défaut : scratchpad/audit).
# Exit code : 0 si zéro pageerror ET toutes les scènes OK ; 1 sinon.
import os, sys, json, time, threading, http.server, socketserver, functools, argparse
from playwright.sync_api import sync_playwright

REPO=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT=8137

ap=argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(REPO,"tools","_audit_shots"))
ap.add_argument("--keep", action="store_true", help="garde le serveur (debug)")
args=ap.parse_args()
os.makedirs(args.out, exist_ok=True)

# --- serveur HTTP silencieux depuis la racine du repo ---
Handler=functools.partial(http.server.SimpleHTTPRequestHandler, directory=REPO)
Handler.log_message=lambda *a, **k: None
httpd=socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL=f"http://127.0.0.1:{PORT}/01_Code/grow_world.html#nointro"

# scènes : (nom, setup JS avant ouverture, JS d'ouverture, sélecteur attendu .show/visible)
SCENES=[
  ("gameplay", "", "", "#iso"),
  ("menu",     "", "menuShow(true)", "#menuwrap"),
  ("pause",    "menuShow(false)", "openPause()", "#pausewrap"),
  ("settings", "openPause&&openPause()", "openSettings&&openSettings()", "#pausewrap"),
  ("seedbar",  "closePause&&closePause();var k=Object.keys(cropCells).filter(x=>cropCells[x].state==='empty')[0];selCell=cropCells[k];", "showSeedbar(true)", "#seedbar"),
  ("carebar",  "var k=Object.keys(cropCells).filter(x=>cropCells[x].state==='empty')[0];var c=cropCells[k];c.state='growing';c.grow=0.5;selCell=c;showSeedbar(false);", "showCarebar(true)", "#carebar"),
  ("workers",  "showCarebar(false);selCell=null;", "openWk()", "#wkmodal"),
  ("missions", "closeWk&&closeWk();", "openMissions()", "#mmodal"),
  ("build",    "closeMissions&&closeMissions();", "openBld()", "#bldmodal"),
  ("home",     "closeBld&&closeBld();", "openHome()", "#homemodal"),
  ("lab",      "closeHome&&closeHome();", "openLab()", "#labmodal"),
]

def hide_all(page):
  page.evaluate("""()=>{['seedbar','carebar','sellbar','wkmodal','mmodal','bldmodal','modmodal',
    'homemodal','labmodal','enmodal','menuwrap','pausewrap'].forEach(id=>{
      const el=document.getElementById(id); if(el)el.classList.remove('show');});}""")

report={"pageerrors":[], "consoleErrors":[], "http404":[], "scenes":{}, "lazy":{}, "offline":{}, "sim":{}}

with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=CHROME)
  ctx=browser.new_context(viewport={"width":393,"height":844}, device_scale_factor=2,
                          is_mobile=True, has_touch=True)
  page=ctx.new_page()
  page.on("pageerror", lambda e: report["pageerrors"].append(str(e)))
  page.on("console", lambda m: report["consoleErrors"].append(m.text) if m.type=="error"
          and "ERR_" not in m.text and "CORS" not in m.text and "404" not in m.text else None)
  page.on("response", lambda r: report["http404"].append(r.url.split("/")[-1]) if r.status==404 else None)
  page.goto(URL); page.wait_for_timeout(1500)
  page.keyboard.press("Shift")   # geste utilisateur -> unlock AudioContext (zéro effet de bord)
  page.evaluate("window.__noModFX=true")
  # débloque toutes les parcelles pour peupler cropCells (comme l'ancien harnais)
  page.evaluate("""()=>{const zs=(typeof W!=='undefined'&&W.cropzones)?W.cropzones:[];
    for(let i=0;i<zs.length;i++)zs[i].owned=true; if(typeof rebuildCrop==='function')rebuildCrop();}""")

  # --- étapes lazy (souples : warn, pas fail) ---
  try:
    page.wait_for_function("()=>Array.isArray(window.WATER_FR)&&WATER_FR.length>=10", timeout=8000)
    report["lazy"]["water_frames"]=page.evaluate("()=>WATER_FR.length")
  except Exception:
    report["lazy"]["water_frames"]=page.evaluate("()=>Array.isArray(window.WATER_FR)?WATER_FR.length:-1")
    report["lazy"]["water_warn"]="WATER_FR n'a pas atteint 10 dans le délai (fallback actif)"
  try:
    page.wait_for_function("()=>window.SND&&SND.ctx&&SND.ctx.state==='running'", timeout=6000)
  except Exception:
    report["lazy"]["audio_warn"]="AudioContext pas 'running' (headless)"
  report["lazy"]["audio_state"]=page.evaluate("()=>window.SND&&SND.ctx?SND.ctx.state:'none'")
  page.wait_for_timeout(1500)
  report["lazy"]["snd_dec"]=page.evaluate("()=>window.SND&&SND.dbg?SND.dbg.dec:-1")
  report["lazy"]["snd_fail"]=page.evaluate("()=>window.SND&&SND.dbg?SND.dbg.fail:-1")

  # --- parcours des scènes ---
  for name, setup, opener, sel in SCENES:
    try:
      hide_all(page)
      if setup: page.evaluate("()=>{"+setup+"}")
      if opener: page.evaluate("()=>{"+opener+"}")
      page.wait_for_timeout(500)
      shown = page.evaluate("(s)=>{const el=document.querySelector(s);if(!el)return false;"
        "return el.id==='iso'?true:(el.classList.contains('show')||getComputedStyle(el).display!=='none');}", sel)
      page.screenshot(path=os.path.join(args.out, f"scene_{name}.png"))
      report["scenes"][name]={"ok":bool(shown), "selector":sel}
    except Exception as e:
      report["scenes"][name]={"ok":False, "error":str(e)}

  # --- scènes conditionnelles (module posé / énergie Domaine≥5) ---
  hide_all(page)
  has_mod=page.evaluate("()=>Array.isArray(window.mods)&&mods.length>0")
  if has_mod:
    try:
      page.evaluate("()=>openModPanel(0)"); page.wait_for_timeout(400)
      report["scenes"]["modpanel"]={"ok":page.evaluate("()=>{const e=document.getElementById('modmodal');return !!e&&e.classList.contains('show');}")}
      page.screenshot(path=os.path.join(args.out,"scene_modpanel.png"))
    except Exception as e:
      report["scenes"]["modpanel"]={"ok":False,"error":str(e)}
  else:
    report["scenes"]["modpanel"]={"ok":True,"skipped":"aucun module posé (état neuf)"}
  hide_all(page)
  hl=page.evaluate("()=>typeof houseLevel!=='undefined'?houseLevel:1")
  if hl>=5:
    try:
      page.evaluate("()=>openEn()"); page.wait_for_timeout(400)
      report["scenes"]["energy"]={"ok":page.evaluate("()=>{const e=document.getElementById('enmodal');return !!e&&e.classList.contains('show');}")}
    except Exception as e:
      report["scenes"]["energy"]={"ok":False,"error":str(e)}
  else:
    report["scenes"]["energy"]={"ok":True,"skipped":f"Domaine {hl} < 5"}

  # --- rétro-compat offline : contexte NEUF + save vieillie injectée AVANT boot (pas de
  # clobber par le pagehide de la page courante) -> load() l'applique au démarrage ---
  SAVE_JS=("try{localStorage.setItem('tinygrow_save_v1',JSON.stringify({v:1,"
    "t:Date.now()-4*3600*1000,coin:1234,stock:80,marketPrice:9,totalHarvest:5000,houseLevel:2,"
    "st:{pl:20},zones:[],land:[],crops:{},wk:{n:2,crew:[['r',600],['v',600]]}}));}catch(e){}")
  ctx2=browser.new_context(viewport={"width":393,"height":844}, device_scale_factor=2,
                           is_mobile=True, has_touch=True)
  ctx2.add_init_script(SAVE_JS)   # s'exécute AVANT les scripts de page, à chaque navigation
  pg2=ctx2.new_page(); pe2=[]; pg2.on("pageerror", lambda e: pe2.append(str(e)))
  pg2.goto(URL); pg2.wait_for_timeout(4500)
  report["offline"]={"coinLoaded":pg2.evaluate("()=>coin"),
                     "crewLen":pg2.evaluate("()=>Array.isArray(window.crew)?crew.length:-1"),
                     "newPageErrors":len(pe2),
                     "loadedOK":pg2.evaluate("()=>coin===1234")}
  ctx2.close()
  browser.close()

httpd.shutdown()

# --- verdict ---
real_404=sorted(set(u for u in report["http404"] if "favicon" not in u.lower()))
report["http404"]=sorted(set(report["http404"]))
scenes_ok = all(v.get("ok") for v in report["scenes"].values())
no_err = len(report["pageerrors"])==0
report["verdict"]={"pageerrors":len(report["pageerrors"]),
                   "scenes_ok":scenes_ok, "console_errors":len(report["consoleErrors"]),
                   "real_404":real_404,
                   "offline_ok": report["offline"].get("newPageErrors",1)==0 and report["offline"].get("loadedOK",False),
                   "green": no_err and scenes_ok and len(real_404)==0 and report["offline"].get("newPageErrors",1)==0 and report["offline"].get("loadedOK",False)}
print(json.dumps(report, indent=2, ensure_ascii=False))
sys.exit(0 if report["verdict"]["green"] else 1)
