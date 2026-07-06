#!/usr/bin/env node
// M4 — passe d'équilibrage des graines payantes.
// Vérifie, PAR VARIÉTÉ, que le rendement net (coin/min) reste positif ET croît avec le tier
// (choix « rendement net vs cadence »). Extrait la table VAR directement de grow_world.html
// (source unique — pas de duplication). Modèle online base : labo 0, maison 0, fert 1, qualité 1,
// pas d'irrigation, aléa moyen 1.0 -> grammes/cycle = varG.
//
// Prix vendu = marketPrice × valueMult × homeSellMult (cf. sellAll). marketPrice ∈ [5,14], MID 9.5.
// On échantillonne 3 prix : bas (5), moyen (9.5 = MKT.MID), haut (14).
const fs=require('fs'), path=require('path');
const HTML=path.join(__dirname,'..','01_Code','grow_world.html');
const src=fs.readFileSync(HTML,'utf8');

// --- extraction single-source de la table VAR ---
const m=src.match(/const VAR=\[([\s\S]*?)\];/);
if(!m){console.error('VAR introuvable dans le HTML');process.exit(1);}
const VAR=Function('"use strict";return ['+m[1]+']')();

const PRICES=[5, 9.5, 14];   // bas / MID / haut (bornes marketPrice + MID)
const fmt=n=>n.toFixed(1).padStart(7);

console.log('\n=== M4 · rendement NET par variété (modèle online base : labo 0, maison 0, fert/qualité 1) ===\n');
for(const price of PRICES){
  console.log(`--- marketPrice = ${price}  (prix/g effectif = ${price}) ---`);
  console.log('  variété    rareté  cycle   g/min   brut c/min  graine/min  NET c/min   vs Verte');
  const verteNet=VAR[0].g/(VAR[0].t/60000)*price;   // Verte gratuite (c=0) = plancher
  let prevNet=-Infinity, monoOK=true;
  VAR.forEach((v,i)=>{
    const cycleMin=v.t/60000;
    const gMin=v.g/cycleMin;
    const grossMin=gMin*price;
    const seedMin=(v.c||0)/cycleMin;
    const netMin=grossMin-seedMin;
    const vsVerte=netMin-verteNet;
    if(i>0 && netMin<prevNet-0.05) monoOK=false;   // doit croître avec le tier (à MID)
    prevNet=netMin;
    const flagPos = netMin>0 ? '' : '  ❌ NON-POSITIF';
    console.log(`  ${v.n.padEnd(9)}  r${v.r}     ${fmt(cycleMin)} ${fmt(gMin)} ${fmt(grossMin)}   ${fmt(seedMin)}   ${fmt(netMin)}   ${(vsVerte>=0?'+':'')+vsVerte.toFixed(1)}${flagPos}`);
  });
  if(price===9.5) console.log(`  -> croissance monotone du NET avec le tier (à MID) : ${monoOK?'✅ OUI':'❌ NON (une variété est dominée)'}`);
  console.log('');
}

// bilan
console.log('=== Bilan ===');
let allPos=true, dominated=[];
VAR.forEach((v,i)=>{
  const cycleMin=v.t/60000, netMID=v.g/cycleMin*9.5-(v.c||0)/cycleMin;
  const verteNet=VAR[0].g/(VAR[0].t/60000)*9.5;
  PRICES.forEach(p=>{ if((v.g/cycleMin*p-(v.c||0)/cycleMin)<=0) allPos=false; });
  if(i>0 && netMID < verteNet-0.05) dominated.push(v.n);
});
console.log('· Idle net-positif à tous les prix testés :', allPos?'✅':'❌');
console.log('· Variétés dominées par la Verte gratuite (à MID) :', dominated.length?('⚠️ '+dominated.join(', ')):'✅ aucune');
console.log('· Coûts actuels :', VAR.map(v=>`${v.n}=${v.c||0}`).join('  '));
console.log('');
