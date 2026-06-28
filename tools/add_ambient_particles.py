#!/usr/bin/env python3
# Ajoute un systeme de particules AMBIANTES (pollen dore + lucioles vertes qui
# flottent) pour un rendu enchanteresque. Systeme SEPARE de `particles` (bursts),
# regle d'or #5 respectee (var global). Insere apres drawParticles() et branche
# dans la boucle draw().
HTML="/home/user/Grow_Room/01_Code/grow_world.html"
h=open(HTML,encoding="utf-8").read()

ANCHOR=("function drawParticles(){ctx.save();for(var i=0;i<particles.length;i++)"
        "{var p=particles[i];ctx.globalAlpha=Math.max(0,p.life);ctx.fillStyle=p.col;"
        "ctx.beginPath();ctx.arc(p.x,p.y,p.sz,0,7);ctx.fill();}ctx.restore();}")
assert h.count(ANCHOR)==1, "ancre drawParticles introuvable/non unique"

AMBIENT=r"""
// === PARTICULES AMBIANTES : pollen dore + lucioles vertes (atmosphere enchantee) ===
var ambient=[];
function spawnAmbient(){
  var target=Math.min(48, Math.round(APP_W*APP_H/14000));
  while(ambient.length<target){
    ambient.push({
      x:Math.random()*APP_W, y:Math.random()*APP_H,
      vx:(Math.random()-0.5)*0.16, vy:-0.08-Math.random()*0.16,
      ph:Math.random()*6.28, sp:0.5+Math.random()*1.1,
      sz:0.7+Math.random()*1.7, t:0, max:7+Math.random()*9,
      col:Math.random()<0.5?'#fff1a8':'#bff0a0'
    });
  }
}
function updateAmbient(){
  var T=performance.now()/1000;
  for(var i=0;i<ambient.length;i++){var a=ambient[i];
    a.x+=a.vx+Math.sin(T*a.sp+a.ph)*0.22; a.y+=a.vy; a.t+=0.016;
    a.life=Math.min(1,(a.life||0)+0.012);
  }
  ambient=ambient.filter(function(a){return a.y>-12&&a.x>-12&&a.x<APP_W+12&&a.t<a.max;});
  spawnAmbient();
}
function drawAmbient(){
  var T=performance.now()/1000; ctx.save();
  for(var i=0;i<ambient.length;i++){var a=ambient[i];
    var tw=0.4+0.6*(0.5+0.5*Math.sin(T*a.sp*1.7+a.ph));
    var fade=Math.min(1,a.life||0)*Math.min(1,(a.max-a.t)/1.5);
    var al=fade*tw*0.6; if(al<=0)continue;
    ctx.fillStyle=a.col;
    ctx.globalAlpha=al*0.30; ctx.beginPath();ctx.arc(a.x,a.y,a.sz*2.6,0,7);ctx.fill();
    ctx.globalAlpha=al;      ctx.beginPath();ctx.arc(a.x,a.y,a.sz,0,7);ctx.fill();
  }
  ctx.restore();
}
spawnAmbient();"""

h=h.replace(ANCHOR, ANCHOR+AMBIENT, 1)

# brancher dans draw() : avant le rendu des bursts
CALL="  updateParticles();drawParticles();"
assert h.count(CALL)==1, "ancre boucle draw introuvable/non unique"
h=h.replace(CALL, "  updateAmbient();drawAmbient();"+CALL.strip()+"\n", 1)

assert h.count('data:image')  # sanity
open(HTML,"w",encoding="utf-8").write(h)
print("OK -> particules ambiantes ajoutees (NON commite)")
