# CLAUDE.md — TINY GROW

> Contexte technique du moteur, à destination de Claude Code et des contributeurs.

---

## 🗣️ Alias & ton

- Claude opère sous l'alias **« Archi »**.
- Ton **casual français**, on se tutoie, surnom **« bro »**.

---

## 🌱 Projet

**TINY GROW — Les Graines de l'Oubli**

- Jeu **idle** de culture de cannabis stylisée.
- Esthétique **« Mystic Nature » / digital-painting**.
- Monde **isométrique 3/4** (style *Hay Day* / *Township*).
- Cible : **mobile portrait 9:16**.
- Fichier de travail : **`01_Code/grow_world.html`** (~88 Ko — moteur seul, **assets externalisés**
  dans `02_Asset/runtime/`).

---

## 🏗️ Architecture du fichier

- Le **moteur** est dans le HTML (le **dernier `<script>`**). Les **assets sont externes**.
- **PACK** = **tableau de clés** (`const PACK = ["plant_v_8", ...]`) + `const ASSET_BASE =
  "../02_Asset/runtime/"`. **255 assets**, chacun un PNG dans `02_Asset/runtime/<clé>.png`
  (dont `home_1..home_11` : les 11 niveaux du domaine de James, dioramas complets ;
  `mod_<ir|nu|cl|en|lo|ce>_<1..5>` : les 30 bâtiments modules v22, calés 1 tuile = 140 px ;
  et `wk_1..wk_40` : les 40 spritesheets personnages v23.5, 64×128).
- `IMG{}` est rempli en bouclant sur `PACK` : `im.src = ASSET_BASE + k + ".png"`.
  Clés des sols via `groundKey()`.
- **Manifest** : `02_Asset/runtime/manifest.json` liste les 255 clés (source de vérité).
- **Histoire/monde** : pipeline de boot — `relocateStarter()` (lopin au centre) →
  `relocateObstacles()` (clairières éloignées du domaine) → `initBonusZones()` →
  `clearWorldToNature()` (zéro bâti humain, sable/pavé→prairie) → `buildRoads()` (3 routes de terre
  qui traversent et se croisent au centre) → `natureFill()` (comble les trous des ex-villages,
  végétation déterministe) → `placeHome()` (`home_<houseLevel>` AU CENTRE `HOME_POS`, parvis +
  couronne décorée).
- **Boucle de rendu** : `function draw()` en `requestAnimationFrame`, **tri de profondeur
  isométrique** par `d = x + y`.

> 💡 **Externalisation (perf remote + Pages)** : le PACK base64 (~30 Mo) a été sorti du HTML
> en 170 PNG raw. Le HTML est passé de ~30 Mo à ~88 Ko → pull/push remote quasi instantanés.
> Les PNG runtime sont des **blobs git normaux** (pas LFS : Pages ne sert pas le LFS).

---

## 🔒 Règles d'or (CRITIQUE — ne JAMAIS oublier)

1. **Clip losange** dans `tile()` :
   `ctx.save()` → path diamant `moveTo`/`lineTo` → `ctx.clip()` →
   `drawImage` avec `ow = w * 1.12` → `ctx.restore()`.
   **NE JAMAIS le perdre.**
2. **Assets externalisés** : pour ajouter/modifier un asset →
   (a) déposer le PNG dans `02_Asset/runtime/<clé>.png` (blob normal, **pas LFS**),
   (b) ajouter la clé au tableau `const PACK = [...]` du HTML **ET** à `manifest.json`.
   ⚠️ Ne **jamais** ré-embarquer de base64 dans le HTML (on casserait tout le gain de poids).
   ⚠️ La clé du tableau doit matcher **exactement** le nom de fichier (casse sensible sous Pages).
3. Ne **JAMAIS hardcoder** couleurs/gradients à la place des vrais atlas — **Nano déteste ça**.
4. **UN changement à la fois**, **validation visuelle** avant de continuer.
5. `particles` doit être un **`var` global**, **pas scoped** dans une fonction.
6. `H(x, y)` doit **`floor`** les coordonnées.
7. Sols **`Sol_1` à `Sol_4`** = PNG **fond blanc** → **détourage blanc-vers-transparent requis**.

---

## ⚙️ Systèmes du moteur (tous présents et câblés)

- **Clip losange** ✓
- **Eau VIVANTE (M1/TINY 6 ✅)** : `waterGen()` (fin de script) génère 10 frames 256² au boot
  (LAZY post-1re-frame, 1 frame/16ms — zéro jank) : `Water_Dif_2.jpg` déformée par sa normal
  map (`dx=(r−128)·amp`), scroll+amplitude sinusoïdaux sur le cycle → boucle PARFAITE,
  grading émeraude in-gen (r×.62 g×.94 b×.90). `WATER_FR[]` global (déclaré AVANT le 1er
  draw), cycle `%N` dans le rendu, guard `okW()` (canvas OU image). ⚠️ Panne (404/CORS) =
  no-op : les `water_f0–f3` v24 restent le fallback À VIE — ne jamais les retirer du PACK.
  Clip losange + crossfade + dégradé de profondeur INTOUCHÉS ✓
- **Vent** (`drawSpWind`) ✓
- **Ombres** (`function shadow`) ✓
- **Fondu d'occlusion 2.0** : un gros objet (`isBig`, `home_*` ET `mod_*` exclus — M2/TINY 6 :
  maison et machines ne s'estompent jamais) ne s'estompe QUE s'il
  recouvre réellement (rects précis + insets PNG + pénétration mini 6px·zoom) un plant vivant,
  `selCell` ou un ouvrier strictement derrière lui — jamais une case vide. Calcul 1×/frame dans
  `draw()` (cibles `fadeTg` → `fadeTgt`), lissage ~190ms (`fadeCur` global, `FADE_MIN=0.38`),
  rampe zoom 0.8→1.05, vent+ancre conservés, zéro `ctx.filter`. ⚠️ Ombres en lock-step avec
  l'alpha BRUT ✓
- **Champs 2.0** : le tapis `parc1-4` est un élément de **passe SOL** (jamais la passe objets —
  sinon il « avale » la base des sprites voisins). Muret `field_border` clippé aux seules arêtes
  EXTÉRIEURES (flags `eN/eE/eS/eW` posés par `rebuildCrop`, adjacence via `cropCells` → zéro
  bordure interne), triangles avant + pentagones arrière (+`hw` pour les tops des blocs), boîte
  calée sur la BASE mesurée de l'anneau (bw 1.014·TW, bh 1.122·TH, ancre 0.55). Portail `fence2`
  unique sur la case SUD de `gateCell` (max x+y, recalculé par rebuildCrop, fallback case champ
  si eau/hors-map) ✓
- **Plantes** : **6 variétés** (`v`/`p`/`b`/`o`/`n`/`a`) × 8 stades → `plant_X_1` à `plant_X_8`.
  **Retune v22** : durée ET rendement PAR VARIÉTÉ (`const VAR`, Verte 60s/6g → Automne
  330s/55g, ±20% d'aléa) — `growCells`/`harvestCell`/`wkOfflineGains` lisent `varT/varG` via
  `c.variety`. Portes en grammes ÷5 (PALIERS, HOUSE.grams, missions 2/3/5/12/17/26/31/38).
  ⚠️ Plus jamais de `GROW_MS`/« 16.5 g » uniques.
- **Modules v22** (GDD « L'Exploitation ») : `mods[{k,lv,x,y,ci,inv}]` sauvé additif,
  `modCells`/`cellMods` runtime recalculés aux 3 événements pose/upgrade/load (JAMAIS par
  frame). Placement libre validé (`modCanPlace`), portées Manhattan 3/4/4/5/6 depuis toute
  case d'emprise, meilleur niveau par case (pas d'empilement), copies ×1.5^ci cap
  2+⌊Domaine/3⌋, portes transitoires en grammes MOD_GATE (Lv3 1600 / Lv4 8000 / Lv5 25000).
  Rendu : ancre au coin SUD de l'emprise, `decScale`/`decYOff` parsent `mod_*`, OcclusionFade
  = **cibles uniquement** (M2/TINY 6 : un arbre devant un module s'estompe, mais le module,
  lui, ne s'estompe jamais — pattern `home_*`). 💧 Irrigation active (drain −1/min, refill vers cap par niveau,
  `irSpd` vitesse ≤ +15% +15% Lv5 — constante `IR_SPD`, source unique code+textes —,
  Sprinklers Lv4+ à la plantation, offline à l'équilibre).
  **UX M2 (TINY 6 ✅)** : `recSpots()` cases vertes recommandées à la pose (calcul 1× à
  `startPlacing`, valeur ajoutée seulement, seuil 0.8·meilleur-POSABLE, `en` exclu) + hint
  1re pose (`stats.mHint` additif) · bandeau bénéfice `modBenefit(k,lv,n)` dérivé de
  `MODS_CFG` (jamais de chaîne dupliquée) dans `tryPlaceAt` (N vivant au tap) · liseré bleu
  passe SOL sur champs couverts via `cmAt` (runtime pur, event-driven — recule en pénurie) ·
  ligne « couvre X · +Y% effectif » dans `openModPanel` (moyenne `irSpd` réelle) · toast
  pédagogique 1re construction (`stats.mFx` additif, setTimeout 2600ms après « construit ! »).
  ⚠️ La qualité reste event-driven (applyCare/wkApplyCare, clamp gCap INVIOLÉ) — la refonte ★
  arrive en v24, ne pas recomputer la qualité dans le tick eau.
- **⚡ Réseau v23** : `enProd/enCons` recalculés par `enRecalc()` aux MÊMES 3 événements que
  `rebuildModCells` (qui construit AUSSI `cellModsDeg`, portées ÷2 pour les Lv2+ — les Lv1
  gratuits gardent tout). Le réseau ne MORD qu'au **Domaine ≥5** (`enOn()`) — jamais de nerf
  rétroactif. Pénurie (`enShort()`) → couverture via `cmAt()` (carte dégradée) + effets ×0.5
  (refill eau, frate fertilité, bonus Lv5). **Overdrive** : +25% vitesse 10 min (`ovSpd()`
  dans growCells), RÉSERVE 150⚡ (comptée dans enShort), cooldown 1h après l'effet, surplus
  ≥150 requis, auto si Energy Core Lv5. Sauvé `en:{e,c}` (timestamps Date.now), `stats.ov`.
- **🌾 Fertilité v23** : `c.fert` 60-140 base 100, PAR CASE (survit à l'état empty, save
  `fert{}` compact ≠100). Récolte −5 (harvestCell) · régén naturelle +0.5/min plafond 85 ·
  module nu `frate` vers `fcap` (batch waterTick 5s) · grammes ×fert/100 (harvestCell ET
  wkOfflineGains via fBar = moyenne (f0+f1)/2 de la FORME FERMÉE drain-récoltes vs régén).
  Teinte de terre en passe SOL (brun fatigué / vert riche). `nfill` au semis ET replant.
  ⚠️ La fertilité ne touche PAS la qualité en v23 (la porte fert>100 → ★4+ arrive en v24).
- **📖 Carnet v1 (v23)** : `computeDiag()`/`updateDiag()` — UNE ligne `#diag` sous le tracker,
  priorité pénurie ⚡ > ≥6 champs sans irrigation > fertilité moyenne <80, hystérésis 5 min,
  « ✅ Réglé » à la résolution. Le Carnet complet (manque à gagner 💰/h) arrive en v28.
- **Anim/FX v22.5** : horloge de frame `FNOW` posée UNE fois en tête de `draw()` — règle :
  code INTRA-draw → `FNOW` ; handlers/intervals/cinématiques HORS-frame → `performance.now()`
  (sinon temps périmé). Émetteurs FX modules 100% **STATELESS** (`drawModFX`, spec
  `anim:[{t,u,v,...}]` par niveau dans `MODS_CFG`, u,v RELATIFS au rect du sprite) : types
  `glow`(générique)/`led`/`shine`/`stream`/`drip`/`mist`, phases hash(x,y,i), dessinés APRÈS
  le drawSp du module à la MÊME profondeur, alpha en lock-step avec le fondu, gates de zoom
  `FX_TIER` (0=toujours · 1≥0.85 · 2≥1.05), budget `fxN` cap 40/frame, porte debug
  `__noModFX`. ⚠️ Ne JAMAIS redessiner le contenu baked des PNG (le jet de l'Arrosoir
  SCINTILLE via 'stream', il n'est pas repeint). `particles` réservé aux ÉVÉNEMENTS
  (cap `MAX_PART=220`, éviction des plus vieilles). Pop d'apparition : `m.bornT` runtime
  (jamais sauvé), `popScale` ease-out-back 450ms ancré à la BASE. `pickMod` = rect de sprite
  (d max = ordre du peintre) puis fallback emprise. Overhead FX mesuré : ~0% (harnais
  verify_v22_fx, 12 tests).
- **Décor** : trees, bushes, flowers, rocks, stumps, bâtiments, rampes, plans d'eau
- **Mon Domaine** : galerie 11 niveaux (`HOUSE`), bonus cumulatifs, cinématique `glideCam` ✓
- **Jardins du Domaine** : mobilier par tier dans `placeHome()` (T1 camp fleuri / T2 cour de
  ferme / T3 esplanade prestige). ⚠️ Slots **safe uniquement** — le diorama fait 4.6 tuiles de
  large : jamais de décor aux diagonales proches (`(2,1)`, `(1,2)`, `(-1,-2)`, `(-2,-1)`…),
  jamais sur les allées E/SW/N ni dans une parcelle (même bonus non achetée) ✓
- **Ouvriers v19** : `WK_CFG`/`workers`/`crew` (persisté `wk:{n,up,crew,b,u2,vs}` additif),
  4 métiers ('r'/'g'/'v'/'f') + XP/niveaux (`wkLvl`, max 5), machine à états au tick 200ms
  (idle/walk/harvest/plant/care/vwalk/sell/patrol/cheer/bwalk/break), identités fixes `WK_ID[8]`
  + pauses hobby, Camp (`CAMP`/`placeCamp()` — Dortoir (48,45) `wkMax()=6+dorm`, Atelier (48,40)
  upgrades `WK_UP2`), marché sinusoïdal `mktDrift()` (cible 9.5±4.5, filtre 0.15/60s, `mt` persisté),
  rendu sprites v23.5 (fallback emoji `JOB_EMO`) + bulles `WK_LINES`, offline par métier
  `wkOfflineGains()` (déterministe, vendeur en formule fermée F/P, XP prorata cap 300).
  ⚠️ Jardinier : ne touche JAMAIS `boosts{}` (soin gratuit plafonné `gCap`, cooldown `c.gcd`
  ré-armé au load). ⚠️ Vendeur : jamais `stats.se/ea`. ⚠️ Le facteur 0.65 de `qOff` = levier
  d'équilibrage anti-méta (teste `[r,r,r,g]>=95%` si tu y touches) ✓
  **Évolution visible (M5/TINY 6 ✅)** : crew étendu ADDITIF `[j,xp,pk,hg,sg]` (lecture
  défensive, vieille save → défauts). Cartes : `wkFxTxt`/`wkCardFx`/`wkSynTxt` (effets dérivés
  des VRAIES formules — ⚠️ wkFxTxt aura = miroir de fmRecalc). Level-up : banner+`sfx_gauge_fill`
  (câblé M5), MAX = `stg_worker_hired`+banner 🏆 (⚠️ `.banner` nowrap+ellipsis ≈30 chars max) ;
  floats « +N XP » agrégés/throttlés 2.5s (`_xpFt` runtime). Badge `stats.wkLu` (pattern mHint).
  Rapport de fierté offline dans `load()` (diff niveaux avant/après `wkOfflineGains`, bannières
  à 5300ms, collective ≥3). **Perks niv 5** : `WK_PERK[8]`, TOUTE lecture via `wkPerk(i)` (null
  si métier ≠ pk[0] — dormance 💤, jamais reset), hooks online+offline symétriques (harvestCell
  pm · wkActMs · wkApplyCare amt/gcd · wkSell lot/vMult(lvl,pb) · fmRecalc `_fm`+`_fmXp`),
  commit atomique `wkPickPerk` (double-tap `.pkbtn`). ⚠️ Cap `vMult ≤1` et `qOff 0.65` INTOUCHÉS.
- **👷 Employés 2.0 (v23.5)** : les ouvriers sont rendus depuis les planches `wk_1..wk_40`
  (64×128) — cellule **20×32** à `sx=col*20, sy=row*32` (⚠️ **JAMAIS** de stride 64/3, les 4 px
  de droite sont vides), rangées **bas/gauche/droite/haut**, **col 1 = idle**, marche = cycle
  `[0,1,2,1]` à 140 ms déphasé par `w.id`. Tenues par MÉTIER : `WK_SPR{r,g,v,f}` (pools
  disjoints, 32/40 planches), pick déterministe `wkSprN(job,id)` = `pool[id%8]` — **zéro save**.
  Les 8 planches grises (5,7,19,21,22,27,29,33) sont **réservées aux clients v25**. Rendu dans
  `drawWorker` : drawImage 9-arg, `imageSmoothingEnabled=false` scopé par save/restore (le
  restore ré-arme le lissage global de resize()), snap entier anti-shimmer, squat harvest/care
  conservé, `wkRow(dx,dy)` grille→rangée (+x→2 · +y→1 · −x/−y→3 · statique→0). ⚠️ Pulse
  d'action, hobby de pause et bulles `wkTalk` sont COMMUNS aux 2 chemins — plus jamais
  d'early-return avant. Fallback emoji conservé (boot avant chargement). Portraits panneau =
  CSS sprite `.labspr` (background-size 96×192, position −30px 0 = col1/row0) via `wkFace(n)` ✓
- **🔊 Audio v24 (É0-É7 COMPLET)** : Web Audio pur, bloc unique après `clamp()` (`SND`/`S()`/
  `SND_TAB`/`SND_LAYERS`). 88 MP3 dans `02_Asset/audio/` (blobs normaux, PAS LFS), **82 câblés**
  — restent au placard : `sfx_grams_pop` (doublon récolte), `sfx_gauge_fill` (pas de trigger),
  `sfx_sprinkler_loop`, `mus_valley_night` (pas de cycle jour/nuit), `amb_campfire_2`/
  `amb_crickets_soft_2`. **`SND_TAB` = seule source de vérité** (schéma
  `{n,l,v,p,t,loop,stg,skipStg,skipAny,vis,p1}` — seules les clés listées sont téléchargées).
  Boot lazy `sndBoot` (rAF+setTimeout fin de script, RIEN avant la 1re frame) ; unlock mobile
  capture+passive ré-armé par `statechange` ; **S() ne joue QUE si `state==='running'`**
  (jamais de sons empilés pré-unlock). Couches `{mus:.18,amb:.30,sfx:.55,wk:.28,ui:.40,stg:.80}`.
  Stingers : exclusifs (skip) + ducking `sndDuck` mus/amb ×0.5 (cibles = CONSTANTES, jamais
  `gain.value` en rampe) ; les enchaînements se font par setTimeout > durée du stinger
  (house_up à +2400ms, dorm_bed à 5400ms). `skipAny` = anti-doublon (ui_toast/banner_in muets
  si un son dédié vient de partir) ; `vis:1` + `{at:cell}` = ouvriers muets hors écran.
  `sndAmbTick` 1×/s : cycle valley_day crossfadé 0.8s (jamais loop=true sur les cyclées),
  rivière/pompe/feu de camp par distance Manhattan à la case CENTRE écran (inverse iso plat),
  grillons si zoom≤0.62, vent 20-60s, suspend batterie à 30s de mute (resume au re-toggle).
  `sndHomeMus` = crossfade openHome↔closeHome. ⚠️ Panne = no-op (404/KO → S() muet) · mute =
  rampe du MASTER · throttles sur `performance.now()` (hors-frame, pas FNOW) · jamais de
  jitter `p` sur un `loop` · clé localStorage SÉPARÉE `'tinygrow_sound'` · `SND.dbg` réservé
  aux harnais (dec/fail/played/pcm/riverG/pumpG/fireG). Toggle 🔊/🔇 = `#sndbadge`
  (flex-shrink:0 !). É0 : queues sfx_/ui_ trimmées, garantie fin-de-contenu@-45dB, rollback
  `git checkout ce00f26 -- <fichier>`.
  **Réglages M6 (TINY 6 ✅)** : volumes UTILISATEUR `SND_VOL{on,mus,amb,fx,ui,wk}` 0..1,
  SOURCE UNIQUE `sndVol(l)` = `SND_LAYERS[l]` × réglage (✨ fx pilote sfx ET stg).
  ⚠️ TOUT restore de gain de couche lit `sndVol(l)`, JAMAIS `SND_LAYERS[l]` (sites :
  sndBoot · sndDuck ×2 · sndMenuDim — sinon le 1er ducking écrase les sliders). Clé
  `'tinygrow_sound'` en JSON `{"on":1,"v":{…}}`, parse défensif ('1'/'0' hérités OK),
  écrite par `sndSaveVol()`. UI = sous-écran `#setpanel` du pause (`#pausewrap.set`),
  sliders live via `sndApplyVol(keys)`, toggle 👷 = multiplicateur wk 0/1, zone danger =
  `gameReset()` (purge les 2 SEULES clés du jeu) en double-tap armé (pattern perks).
  **Mixage spatial M7 (TINY 6 ✅)** : `SND_ZMIX{mus,amb}` (runtime) PLIÉ dans `sndVol(l)`
  → compose partout gratuitement (sliders/duck/menuDim). Courbes dans `sndAmbTick` (après
  la porte menu) : k=(zoom−0.4)/1.3 → mus 1−0.65k · amb 0.7+0.3k, retarget 0.4s si Δ>0.01
  ET hors-duck (mid-duck : le restore lit le sndVol à jour). One-shots positionnés dans
  `S()` : gain `1−(d/R)²` (R=0.9·APP_H, skip ≤0.02) + StereoPanner ±0.4 (fallback = chaîne
  inchangée), `SND.dbg.sp={g,pan}` pour les harnais. ⚠️ Jamais de spatialisation sans
  `o.at` (gestes joueur/UI/stingers/musique). ⚠️ Boucles rivière/pompe/feu volontairement
  NON migrées (déjà graduées par distance, tuning v24 validé). ~110 Mo de PCM décodé (mus 120s ≈ 42 Mo) — échappatoire
  décodage-à-la-demande si un mobile souffre. Harnais : verify_audio.js 48/48.
- **Missions** : chaîne `MISSIONS[53]` (8 chapitres — **append strict**, indices historiques gravés
  dans les saves) + compteurs `stats{}`, tracker `.mtrack` + modal `#mmodal`, claim atomique,
  save `{mi,st}` additif ✓
- **🎬 L'Ouverture (M8/TINY 6)** : intro splash → menu principal → jeu. Markup STATIQUE dans
  le body (1er paint = noir-violet, `if1` part avant le storm PACK) ; machine à états
  `INTRO{st,boot,menuOn,tmr,entering}` + `introGo()` = setTimeout UNIQUE chaîné + transitions
  CSS (zéro rAF ajouté) ; partition gravée : noir 400 → f1 800/2000/700 → f2 800/2400 →
  menux 1200 (cascade .menuin délais 0/.15/.3s) ; skip = click #intro → menux. Z-index :
  `#intro` 70 · `#menuwrap` 65 · `#pausewrap` 61 (au-dessus du z60 flash/fcoin). Ken Burns =
  `kbpan` 20s ease-in-out alternate (±6% translate). Lucioles = 15 divs GPU (transform/opacity,
  JAMAIS de filter/blur). ⚠️ PORTE `INTRO.menuOn` en tête de `sndAmbTick` : la vallée ne
  démarre JAMAIS sous le titre (et sert de retry 1×/s pour `mus_menu_home`, `p1:1`).
  ⚠️ La cascade « bon retour » de `load()` est enveloppée dans `_welcome` et part à
  `enterGame()` (glideCam d'arrivée = `INTRO.boot` une seule fois). `menuShow(bool)` =
  aussi le retour titre depuis le pause (jamais les splashs). Pause : `openPause/closePause`,
  la simu ne se fige JAMAIS (intervals wall-clock). ⚠️ Câblage des boutons AVANT le
  early-return `#nointro` (hook harnais : boot direct strictement v24 — toutes les scenes
  Playwright l'utilisent sauf m8). ⚠️ `Fond_?.png` exclus du LFS par règle .gitattributes
  dédiée (blobs web sains, mais le pattern `02_Asset/**/*.png` les matcherait au re-commit).
  ⚠️ Le bouton Cultiver pulse en boucle → `tap(force=True)` dans les tests Playwright.

---

## 🧪 Workflow de test

1. **Extraire le dernier `<script>`** : `a = rfind('<script>') + 8`, `b = find('</script>')`,
   puis `node --check`.
2. **Playwright screenshot** : **393×844**, **DPR 2**, contexte **`has_touch` + `is_mobile`**.
3. **Toujours valider visuellement avant de livrer.**

---

## 🎨 Assets sources à intégrer (dans `02_Asset/`)

| Fichier | Contenu |
|---|---|
| `Glow_Arbre.png` | **12 arbres premium** (chêne, érable, bouleau, pommier, sapin, saule, cerisier) |
| `Glow_Maison.png` | **20 bâtiments** (maisons colombages, serres verre, abris) |
| `Glow_Plante.png` | **6 variétés cannabis × 8 stades** (graine → bourgeon), couleurs variées |
| `Glow_Terrain.png` | **Déco** (buissons, rochers, souches, champignons, étangs, fleurs, sols, clôtures) |
| `Grow_Water_1.png` | **Spritesheet eau émeraude 2×2** |

---

## 📁 Structure des dossiers

```
Grow_Room/
├── 01_Code/
│   └── grow_world.html       # Le moteur iso (~88 Ko) — charge les assets externes
├── 02_Asset/                 # Atlas sources Glow_* (LFS, dev only)
│   └── runtime/              # 170 PNG servis au jeu (blobs normaux, PAS LFS) + manifest.json
├── README.md
├── CLAUDE.md                 # Ce fichier
├── .nojekyll                 # Pages sert les fichiers bruts
├── .gitattributes            # LFS pour atlas Glow_* / runtime/ forcé hors-LFS
└── .gitignore
```
