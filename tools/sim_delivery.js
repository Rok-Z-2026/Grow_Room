#!/usr/bin/env node
// M3 — équilibrage du canal LIVRAISON.
// Point clé : la livraison convertit le stock en pièces au PRIX MARCHÉ exact
// (marketPrice·valueMult·homeSellMult), sans prime -> ZÉRO inflation : le total de coin est
// borné par production×prix, comme la vente manuelle/vendeur. La livraison n'est que de
// l'AUTOMATISATION (cadence longue), pas une source de valeur neuve.
// Cette sim montre le DÉBIT passif max (g/min et coin/min) par niveau de Maison, pour
// vérifier qu'il reste un supplément raisonnable (jamais un remplaçant du jeu actif).
// Extrait VEH_TIER + DELIVER_CD du HTML (source unique) ; vehCap miroir de 80+40·tier.
const fs=require('fs'), path=require('path');
const src=fs.readFileSync(path.join(__dirname,'..','01_Code','grow_world.html'),'utf8');

const tierM=src.match(/const VEH_TIER=\[([^\]]*)\]/);
const cdM=src.match(/DELIVER_CD=(\d+)/);
const capM=src.match(/function vehCap\(tier\)\{return (\d+)\+(\d+)\*tier;\}/);
if(!tierM||!cdM||!capM){console.error('constantes M3 introuvables dans le HTML');process.exit(1);}
const VEH_TIER=JSON.parse('['+tierM[1]+']');
const CD_MIN=(+cdM[1])/60000;                       // cooldown en minutes
const vehCap=t=>(+capM[1])+(+capM[2])*t;

const PRICES=[5,9.5,14];   // bas / MID / haut

console.log('\n=== M3 · débit MAX du canal livraison (si le stock suit) ===');
console.log(`cooldown=${CD_MIN.toFixed(2)} min · cap=${capM[1]}+${capM[2]}·tier · vente au PRIX MARCHÉ\n`);
console.log('Maison  tier  cap(g)  g/min   coin/min @5   @9.5    @14');
for(let hl=1;hl<=11;hl++){
  const tier=VEH_TIER[hl-1], cap=vehCap(tier), gmin=cap/CD_MIN;
  const c=PRICES.map(p=>Math.round(gmin*p));
  console.log(`  ${String(hl).padStart(2)}    ${String(tier).padStart(2)}   ${String(cap).padStart(4)}   ${gmin.toFixed(1).padStart(5)}   ${String(c[0]).padStart(6)} ${String(c[1]).padStart(6)} ${String(c[2]).padStart(6)}`);
}
console.log('\n· Débit PLAFOND (le vrai débit = min(production, ce plafond)).');
console.log('· Vente au prix marché -> aucune prime, aucune inflation : borne = production×prix.');
console.log('· Cadence longue (1 livraison / '+CD_MIN.toFixed(1)+' min) -> supplément d\'automatisation, pas un méta.\n');
