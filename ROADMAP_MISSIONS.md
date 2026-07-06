# 🗺️ ROADMAP MISSIONS — TINY GROW v23+
### Les 5 prochains chantiers — plans détaillés pour le CLI

> **Source** : notes de Nano (05/07/2026) + sondage complet de `grow_world.html` v22 par Archi.
> Chaque mission est **autonome** : elle se traite séparément, dans un sprint dédié.
> **Une seule mission active à la fois** — Nano choisit l'ordre et donne le GO.

---

## ⛔ RÈGLES ABSOLUES (pour chaque mission)

1. **DIAGNOSIS-FIRST** : avant de coder, le CLI relit la section « État actuel » ci-dessous,
   vérifie dans le code, et **propose son plan d'exécution détaillé**. Aucune ligne de code
   avant le GO de Nano.
2. **One change at a time** : chaque étape = un changement visible, capturé (Playwright
   390×844 DPR2) et validé par Nano avant la suivante.
3. **Zéro régression** : ne jamais toucher aux systèmes voisins. Les saves existantes
   doivent continuer de fonctionner (rétro-compatibilité obligatoire).
4. Syntaxe JS vérifiée (`node -e` + `vm.Script`) après chaque édition.
5. `CLAUDE.md` et `GAME_BIBLE.md` restent les références. Mettre à jour la Bible à la fin
   de chaque mission terminée.

**Ordre suggéré par Archi** (quick wins d'abord, Nano décide) :
M2 (S/M) → M5 (M) → *sprint audio de base (AUDIO_HANDOFF)* → M8 (M/L) → M6 (M) → M7 (M) → M1 (M/L) → M4 (L) → M3 (L/XL)

**Décisions design : TOUTES TRANCHÉES ✅** (par Nano & Archi, critère : le rendu le plus
beau possible). Le CLI n'a plus aucune question à poser — chaque mission contient ses
décisions finales, il ne reste que le diagnostic technique et le GO de Nano par étape.

---

## 📋 TABLEAU DE SUIVI (le CLI le met à jour, dans l'ordre suggéré)

| # | Mission | Effort | Statut | Fini le | Note |
|---|---------|--------|--------|---------|------|
| M2 | Machines : visibilité, guidage, utilité | S/M | ✅ Terminée | 2026-07-06 | Machines 100% opaques (isBig) · cases vertes recommandées + hint 1re pose · bandeau bénéfice ghost (N champs vivant, % réel par niveau) · liseré bleu permanent champs couverts (cmAt, recule en pénurie ⚡) · « couvre X champs · +Y% effectif » au panneau · toast pédagogique 1re construction |
| M5 | Employés : évolution visible | M | ✅ Terminée | 2026-07-06 | Cartes enrichies (palier suivant chiffré, carrières 🌿/🧺, synergies Camp) · fête du level-up (banner+son, 🏆 au MAX) · badge ⭐ persistant · rapport de fierté offline · 8 perks niv 5 à personnalité (save additive `[j,xp,pk,hg,sg]`, garde-fous intacts) — journal détaillé dans la section M5 |
| 🎧 | Sprint audio de base (`AUDIO_HANDOFF.md`) | M | ✅ Terminée | 2026-07-05 | v24 É0-É7 « La Vallée qui chante » — 82/88 MP3 câblés (commits `ce00f26..ec58645`) |
| M8 | Menu principal & menu pause | M/L | ⬜ À faire | — | Prérequis LEVÉ : `Fond_1/2/3.png` présents dans `02_Asset/` |
| M6 | Menu du jeu + réglages son | M | ⬜ À faire | — | Dépendance levée : AudioManager v24 en place (`SND_LAYERS`) |
| M7 | Mixage spatial | M→S/M | ⬜ À faire | — | ~70% couvert par v24 : gain-distance rivière/pompe/feu (`sndProx`/`sndAmbTick`), gating hors-écran `vis:1`, grillons zoom≤0.62. Reste : courbe musique↔zoom, gain graduel des sfx ouvriers (aujourd'hui binaire), pan stéréo optionnel |
| M1 | Eau vivante (fake shader) | M/L | ⬜ À faire | — | Prérequis LEVÉ : `Water_Dif_1/2` + `Water_NRM_1/2` présents dans `02_Asset/` (⚠️ en **.jpg**, pas .png) |
| M4 | Graines payantes | L | ⬜ À faire | — | — |
| M3 | Chemin des livraisons (véhicules) | L/XL | ⬜ À faire | — | — |

Statuts : ⬜ À faire · 🔵 En cours (**une seule à la fois, jamais deux**) · ✅ Terminée.
Quand une mission passe ✅ : date + note d'une ligne (ce qui a été livré) + commit.

## 🔄 CYCLE DE VIE DE CE DOCUMENT
1. **Une mission à la fois, une feature à la fois** : le CLI passe la mission en 🔵,
   diagnostique, propose son plan, attend le GO de Nano, puis exécute étape par étape
   (chaque étape validée visuellement par Nano avant la suivante).
2. **Mission validée et finie** → statut ✅ dans le tableau + date + note + commit, et la
   section correspondante de `GAME_BIBLE.md` est mise à jour dans la foulée.
3. **Quand les 9 lignes sont ✅** : l'essentiel est reporté dans `GAME_BIBLE.md` /
   `CLAUDE.md`, puis **ce fichier est SUPPRIMÉ du repo** — il est jetable par design,
   c'est un document de chantier, pas d'archive.

---

# 🌊 MISSION 1 — Eau vivante : shader avec vagues et reflets

## 🎯 Objectif
Remplacer l'eau actuelle par une eau **dynamique et animée** : vagues, reflets, mouvement
continu — en utilisant les textures `Water_Dif_1/2.jpg` déformées par leurs Normal Maps
`Water_NRM_1/2.jpg`. Le tout compatible **HTML/canvas mobile** (pas de moteur 3D).

## 📍 État actuel dans le code
- L'eau est rendue par **4 frames de tuiles runtime** (`water_f0..f3` dans le PACK) avec
  phase par case + crossfade, plus une texture `waterTex` de fond.
- Le pipeline assets passe par `02_Asset/runtime/` (ASSET_BASE ligne 270).
- ✅ **Prérequis levé (05/07/2026)** : `Water_Dif_1/2.jpg` et `Water_NRM_1/2.jpg` sont dans
  `02_Asset/` (⚠️ format **.jpg** — pas de transparence, à prendre en compte au découpage).

## 🧭 Deux approches possibles (le CLI diagnostique et recommande, Nano tranche)

**Option A — « Fake shader » canvas 2D (recommandée par Archi)**
Pas de WebGL : au boot, on **précalcule 8 à 12 frames** d'eau en offscreen canvas en
déformant la diffuse avec la normal map (offset UV : `dx = (NRM.r-128)*amp`,
`dy = (NRM.g-128)*amp`, avec `amp` qui ondule dans le temps) + une couche de reflets
(highlights extraits de la NRM, additive blending, scroll lent).
→ On remplace juste `water_f0..f3` par ces frames générées : **zéro changement du pipeline
de rendu existant** (phase/crossfade conservés). Coût boot ~100-200 ms, ensuite gratuit.

**Option B — Canvas WebGL dédié à l'eau**
Un vrai fragment shader (diffuse + NRM + temps) sur un second canvas composé sous le
canvas 2D, clippé aux zones d'eau. Rendu superbe mais : gestion double-canvas, sync caméra/
zoom, risques de perf sur mobile bas de gamme, complexité ×3.

## 🪜 Plan par étapes (si Option A)
1. Vérification des 4 JPG uploadés (dimensions, tuilable ?).
2. Prototype offscreen isolé : générer 1 frame déformée, capture, validation du look.
3. Génération des 8-12 frames au boot + injection dans le PACK à la place de `water_f0..f3`.
4. Réglage amplitude/vitesse/reflets (2-3 itérations visuelles avec Nano).
5. Test perf mobile (FPS au zoom large), fallback : réduire le nombre de frames.

## ✅ Validation
Captures avant/après sur la rivière + l'étang, FPS stable, l'eau « vit » même caméra immobile.
**Effort : M/L**

---

# 🏗️ MISSION 2 — Machines : visibilité, guidage, utilité claire

## 🎯 Objectif
Trois problèmes UX constatés par Nano à corriger :
1. Les machines deviennent **transparentes quand la caméra s'approche** (comme les arbres).
2. Quand on sélectionne une machine dans le menu 🏗️, **on ne sait pas où la poser ni quoi
   faire** — le joueur est perdu.
3. On ne comprend pas **à quoi servent les machines** : leur rôle dans la progression doit
   être évident et chaque machine doit apporter un bénéfice concret et lisible.

## 📍 État actuel dans le code
- **Transparence** : le fondu de proximité/zoom (`fadeCur` / `fadeAlpha`, lignes ~1447+)
  s'applique aux sprites verticaux. La maison est explicitement **exclue** du fondu
  (« jamais estompée », règle Bible) — les modules, eux, le subissent. → Fix : les exclure
  du fade comme la maison. *(Le CLI confirme au diagnostic que c'est bien ce chemin.)*
- **Guidage de pose** : il existe déjà un ghost avec halo de couverture (`startPlacing`,
  `tryPlaceAt`, `confirmPlace`) — mais rien n'indique OÙ c'est malin de poser (près des
  champs), ni de tuto première pose.
- **Utilité** : l'Irrigation a de vrais effets (+15% pousse, sprinklers…) mais ils sont
  enfouis dans le panneau. **Trois familles sont achetables** (💧 Irrigation · 🌾 Nutriments ·
  ⚡ Énergie, `av:1` en v23) — 📦/👷/🌡️ restent « 🚧 Bientôt ». La mission VIII
  « L'Ingénieur » guide déjà vers le 1er module.

## 🪜 Plan par étapes
1. **Fix transparence** : exclure les cases modules du système de fade (pattern maison).
   → capture avant/après en zoom proche. *(Quick win, 1 seule édition.)*
2. **Guidage de pose intelligent** : en mode placement, surligner en vert doux les
   emplacements **recommandés** (cases à ≤ portée d'un max de champs owned, score simple),
   + flèche/pulse « 📍 pose-moi près de tes champs » à la 1re pose (pattern `missionGuide`).
3. **Bandeau bénéfice au survol/ghost** : afficher en clair l'effet concret AVANT l'achat :
   « 💧 +15% de vitesse de pousse sur 8 champs couverts ».
4. **Feedback d'utilité permanent** : petit indicateur sur les champs couverts (goutte
   discrète / liseré bleu) pour VOIR la machine travailler, + ligne dans le panneau module :
   « couvre X champs · +Y% pousse effectif ».
5. **(Validé ✅)** Toast pédagogique à la 1re construction : « Tes plants couverts
   poussent +15% plus vite ! ».

## ✅ Validation
Un nouveau joueur comprend en < 10 s où poser et pourquoi ; les machines restent opaques
de près ; l'effet est visible sur le terrain. **Effort : S/M**

---

# 🚚 MISSION 3 — Le Chemin des Livraisons : véhicules évolutifs

## 🎯 Objectif
Créer un **chemin qui sort de la map** et rejoint le centre, près de la maison de James.
Des **véhicules viennent chercher la beuh** et repartent : d'abord un vélo, puis vélo
motorisé → scooter → moto → voiture… Plus le joueur progresse, plus les véhicules sont
gros, rapides, impressionnants — une vraie sensation de montée en puissance.

## 📍 État actuel dans le code
- `buildRoads()` construit déjà 3 routes de terre qui **se croisent près de chez James**
  (`HOME_POS` au centre) — le carrefour existe, il suffit de prolonger une branche jusqu'au
  bord de la map (cases `path` jusqu'à x=0 ou y=87).
- Il n'existe **aucun système de véhicules** ; mais les ouvriers marchent déjà case par
  case (`tickWk`) → le moteur de déplacement sur grille est réutilisable comme base.
- Synergie design évidente : le **Vendeur 🤠** vend déjà par lots — le véhicule peut
  devenir la **matérialisation visuelle des ventes** (le lot part physiquement !).
- ⚠️ Aucun sprite de véhicule dans le PACK → **Nano doit générer les assets**
  (vélo, vélo moteur, scooter, moto, voiture… vue iso 3/4, fond noir pur, 2 directions).

## ✅ Décisions tranchées (critère : le plus beau)
1. **Cosmétique d'abord** : le véhicule est le spectacle des ventes, il ne bloque rien.
   *(Version gameplay « les ventes partent avec le véhicule » = éventuelle v2, sprint
   séparé, seulement si le rythme s'y prête.)*
2. **Déblocage par niveau de maison** — le totem de progression du jeu, lisible d'un
   coup d'œil : la maison grandit, le garage suit.
3. **5 paliers** : 🚲 vélo (maison 1) → 🚲⚡ vélo motorisé (3) → 🛵 scooter (5) →
   🏍️ moto (7) → 🚗 voiture (9). Chaque déblocage = toast événement + le nouveau
   véhicule fait son premier trajet dans la foulée (le moment de fierté).

## 🪜 Plan par étapes
1. **Le chemin** : prolonger une route existante jusqu'au bord de la map (choix du bord
   avec Nano sur capture), en respectant rivières/ponts. Validation visuelle seule.
2. **Assets véhicules** : Nano génère, pipeline `tools/` habituel vers le runtime.
3. **Moteur de trajet** : un « runner » qui spawn au bord, suit le chemin case par case
   jusqu'au parvis (réutilise la logique de marche ouvrier), petite pause « chargement »
   (animation + particules), puis repart. Z-order + ombre comme les ouvriers.
4. **Branchement au Vendeur/ventes** : un trajet se déclenche à chaque vente (throttle :
   max 1 véhicule en route, file d'attente sinon).
5. **Évolution** : table `VEHICLES[palier]` (sprite, vitesse, capacité visuelle), toast
   d'événement au déblocage : « 🛵 Un scooter livre maintenant ta production ! ».
6. *(Plus tard, hors mission)* : sons `sfx_vehicle_*` à ajouter au pack audio.

## ✅ Validation
Un véhicule traverse la vallée du bord jusqu'à chez James, charge, repart ; le palier
suivant se débloque et se voit. Zéro impact sur l'éco. **Effort : L/XL**

---

# 🌱 MISSION 4 — Graines payantes : ralentir intelligemment

## 🎯 Objectif
Mettre en place une **limite par graine** : le joueur doit **acheter ses graines** pour
progresser. Chaque graine a ses caractéristiques (rareté, rendement, temps de pousse,
conditions de réussite). Créer des variantes pour forcer des **choix stratégiques** —
ralentir la progression tout en donnant une vraie sensation d'évolution.

## 📍 État actuel dans le code
- Les graines sont **explicitement GRATUITES** (retune v22, ligne ~296) — les 6 variétés
  n'ont ni coût ni stock, la seedbar plante à volonté.
- Les variétés ont déjà durée/rendement différenciés (v22 : 6 g/1 min → 55 g/5 min 30,
  ±20% d'aléa) — la **base « caractéristiques » existe**, il manque coût + rareté +
  éventuelles conditions.
- ⚠️ **Gros impact d'équilibrage** : missions du chapitre I (« Plante 3 graines »),
  économie du début de partie (le joueur démarre avec quelques pièces), auto-replant des ouvriers
  (replantent la même variété — gratuit ? payant ? sinon l'idle casse), offline.
- ⚠️ **Rétro-compat saves** : un vétéran ne doit pas se retrouver bloqué sans graines.

## ✅ Décisions tranchées (critère : le plus beau ET le plus sain)
1. **Coût à la plantation** (v1) : la seedbar affiche simplement le prix sous chaque
   variété, grisée si pas assez 💰. Zéro UI nouvelle, zéro friction. *(L'inventaire de
   graines en lots = éventuelle v2.)*
2. **Les ouvriers paient la graine** en replantant, déduction automatique — coût
   calibré très en dessous de la valeur de récolte pour que l'idle reste toujours
   positif. Sinon les graines payantes deviennent décoratives dès le 1er Récolteur.
3. **Rareté = habillage, PAS de taux d'échec** : tags visuels commun → rare → épique →
   légendaire (couleur du cadre + étoiles sur la seedbar — c'est joli ET informatif).
   Les « conditions de réussite » restent les soins existants (eau/soleil/sérum → qualité).
   Aucune frustration aléatoire sur mobile.
4. **La graine 🟢 verte reste gratuite à vie** — filet de sécurité anti-blocage absolu :
   quoi qu'il arrive, on peut toujours planter, jamais de game over économique.

## 🪜 Plan par étapes
1. Table `SEED_COST[variety]` + affichage prix sur la seedbar (grisé si pas assez 💰).
2. Déduction à la plantation (joueur ET ouvriers) + `ui_denied` si fauché + garde-fou
   anti-blocage (verte gratuite OU prêt automatique si coin=0 et champ vide).
3. Passe d'équilibrage : simulation g/min net par variété (script jsdom), ajustement pour
   que la courbe reste fun (le choix devient rendement net vs cadence).
4. Rétro-compat : missions chapitre I inchangées (la verte gratuite les protège), test
   vieille save.
5. *(Extension, sprint séparé)* : raretés + nouvelles variantes + lien avec le futur labo
   de croisement (Bible §5) — les hybrides deviennent LA source des graines rares.

## ✅ Validation
La progression en début de partie est sensiblement plus posée sans jamais bloquer ; l'idle reste positif ;
une vieille save joue normalement. **Effort : L**

---

# 👷 MISSION 5 — Employés : évolution VISIBLE et motivante

## 🎯 Objectif
Que chaque employé **progresse** (vitesse, efficacité, spécialisation, impact) et que le
joueur ait **envie** de les garder, les améliorer, les spécialiser — que l'équipe devienne
une vraie fierté de progression.

## 📍 État actuel dans le code — ⚠️ LE SYSTÈME EXISTE DÉJÀ (v19), il est juste INVISIBLE
- XP par action : récolte +2 · soin +1 · vente +10 · aura +1/5 cycles (`wkGainXp`).
- Niveaux 1→5 (seuils 60/240/540/1200), effets réels par niveau et par métier :
  récolteur −5% temps/niv · jardinier +cap qualité · vendeur +prix · contremaître +aura.
- 4 métiers réassignables, identités fixes (Marcel, Brume, Gégé…), XP offline capée.
- **Le problème** : presque rien de tout ça n'est montré au joueur → d'où l'impression
  que les employés sont « achetés puis oubliés ». La mission est d'abord une mission
  d'**UI/feedback**, puis d'extension.

## 🪜 Plan par étapes
1. **Cartes ouvriers enrichies** (panneau 👷) : barre d'XP animée, niveau ⭐, prochain
   palier chiffré (« Niv 3 → −15% temps de récolte »), total récolté/vendu par perso.
2. **Feedback monde** : « +2 XP » flottant discret sur l'ouvrier qui agit (throttlé),
   **banner + son au level-up** (« ⭐ Marcel passe niveau 3 ! ») — le moment de fierté.
3. **Badge d'alerte** sur le bouton 👷 quand un ouvrier vient de monter de niveau.
4. *(Extension 1 — validée ✅)* **Perk au niveau 5** : un choix unique par perso
   (ex. Marcel niv 5 : « Bras de boulanger » +10% rendement de SES récoltes) — de la
   personnalité, pas juste des stats.
5. *(Extension 2 — validée ✅)* Synergie avec les upgrades Camp existants (Manuel de l'ouvrier +XP…) :
   les rendre visibles sur les cartes (« +15% XP actif »).

## ✅ Validation
En ouvrant le panneau 👷, on voit qui progresse et pourquoi ; un level-up se FÊTE à
l'écran ; le joueur cite spontanément son ouvrier préféré. **Effort : M**

## 📓 Journal de bord M5 (mis à jour à CHAQUE étape — on ne se perd jamais)
> Décisions gravées : perk lié à l'IDENTITÉ (dormant si réassigné, jamais reset) ·
> save additive `[j,xp,pk,hg,sg]` · sons SANS nouveau MP3 (`sfx_gauge_fill` câblé +
> réemploi `stg_worker_hired` au MAX) · qOff 0.65 et tous les garde-fous INTOUCHÉS.

✅ É1 Cartes enrichies (effet courant + prochain palier chiffré + synergies Camp) — wkFxTxt/wkCardFx/wkSynTxt, capture m5_e1 OK
✅ É2 Compteurs de carrière (🌿 récolté / 🧺 vendu par perso, online + offline) — tuple `[j,xp,pk,hg,sg]`, rétro-compat testée (save pré-M5 → défauts propres)
✅ É3 Feedback monde (+XP throttlé/agrégé 2.5s · banner+`sfx_gauge_fill` au level-up · 🏆+`stg_worker_hired`+double burst au MAX) — captures m5_e3a/b/c
✅ É4 Badge ⭐ sur le bouton 👷 (persisté `stats.wkLu`, bounce mgift, éteint à l'ouverture) — capture m5_e4
✅ É5 Rapport de fierté offline (bannières séquencées à 5.3s, collective ≥3, MAX individuel) — testé bout-en-bout avec save vieillie de 4h, captures m5_e5_max/collectif
✅ É6 Perk niveau 5 (WK_PERK 8 dons, wkPerk() gate par métier, double-tap confirmé, dormance 💤, hooks online+offline, cap vendeur ≤1 vérifié, round-trip save OK) — captures m5_e6/e6b
✅ É7 Clôture (journal ✅ · table ✅ · GAME_BIBLE · CLAUDE.md · commit + push)

---

# ⚙️ MISSION 6 — Menu du jeu + Réglages Son complets

## 🎯 Objectif
Le jeu n'a **aucun menu** : en créer un (bouton ⚙️ dans la topbar) qui devient la maison
des réglages — avec en vedette un **panneau Son** pour tout gérer : mute global et volume
de chaque famille de sons, réglages persistés.

## 📍 État actuel dans le code
- **Aucun menu de jeu n'existe** (vérifié : seuls les panneaux lab/wk/missions/home/bld).
  La sauvegarde est 100% auto (localStorage), il n'y a ni bouton settings, ni à-propos.
- Le pattern de panneau plein écran existe déjà (`openLab`/`close*`) → à réutiliser tel
  quel pour rester cohérent visuellement.
- ⚠️ **Dépendance** : les sliders de volume pilotent les GainNodes par couche du futur
  AudioManager (`AUDIO_HANDOFF.md`, étapes 1-2). Le menu peut naître avant (structure +
  mute), mais le panneau Son complet nécessite le manager en place.
- 🔗 **Lien avec la Mission 8** : ce panneau Réglages a vocation à devenir un sous-écran
  du **Menu Pause** (M8). S'il est livré avant, il vit provisoirement derrière le bouton
  ⚙️, puis M8 le rhabille dans la DA sans changer sa logique.

## 🪜 Plan par étapes
1. **Bouton ⚙️ + panneau Menu** (pattern des panneaux existants) avec sections vides
   prêtes : 🔊 Son · ℹ️ À propos (version, crédits Nano Studio) · 🧨 Zone danger.
2. **Panneau Son** : mute global 🔇 + **4 sliders** — 🎵 Musique · 🌿 Ambiances ·
   ✨ Effets (gestes, monde, stingers) · 🖱️ Interface — branchés sur les GainNodes,
   changements audibles en direct, valeurs persistées en localStorage et appliquées au boot.
3. **Zone danger** : « Réinitialiser la partie » avec **double confirmation** explicite
   (impossible à déclencher par accident) — utile pour les tests de Nano aussi.
4. **(Validé ✅)** Toggle « Sons des ouvriers » séparé, pour ceux qui veulent la
   vallée calme.

## ✅ Validation
Le menu s'ouvre/ferme proprement sur mobile ; chaque slider s'entend immédiatement ;
un kill de l'app puis relance conserve les réglages. **Effort : M**

---

# 📡 MISSION 7 — Mixage spatial : le son vit avec la caméra

## 🎯 Objectif
Que le volume **réagisse à la caméra** :
1. **Musique liée au zoom** : dézoomé loin au-dessus de la map → la musique porte
   (contemplation) ; zoomé près du sol → elle s'efface en douceur et laisse la place aux
   sons du monde (immersion).
2. **Sons du monde spatialisés** : tout son émis à un endroit de la map (ouvrier qui
   récolte, pompe, sprinkler, rivière, véhicule plus tard…) est **atténué selon sa
   distance** au centre de la caméra — proche = net, loin = discret, hors champ = coupé.

## 📍 État actuel dans le code
- Le zoom et la caméra existent (`zoom`, `cam.x/y`, `clampCam`, conversions `isoX/isoY`
  case→écran) → tout ce qu'il faut pour calculer une distance écran est déjà là.
- L'atténuation par distance était déjà esquissée pour `amb_river` dans `AUDIO_HANDOFF.md` ;
  cette mission **généralise** le principe à tous les sons du monde.
- ⚠️ **Dépendance** : nécessite l'AudioManager (AUDIO_HANDOFF étapes 1-3). Ses hooks
  doivent être prévus dès sa conception — note ajoutée dans le handoff.

## 🧭 Règles de mixage (la spec)
- **Musique ↔ zoom** : gain musique = interpolation douce entre ×1.0 (zoom min / vue
  large) et ×0.35 (zoom max / près du sol), avec ramp ~400 ms à chaque changement de zoom
  (jamais de saut sec). Les ambiances font le chemin inverse en léger (×0.7 loin → ×1.0
  près) pour que la vallée « monte » quand on s'approche.
- **Spatialisation** : `play(son, {at:{x,y}})` → volume = 1 − (distance écran au centre /
  rayon audible)², borné [0, 1] ; au-delà du rayon (± une marge hors écran), le son n'est
  **pas joué du tout** (économie CPU). Bonus léger : pan stéréo selon la position
  horizontale à l'écran (StereoPannerNode, subtil : ±0.4 max).
- **Jamais spatialisés** : les actions du joueur lui-même (planter/soigner/récolter au tap),
  l'UI, les stingers et la musique — c'est SON geste, il doit rester plein et net.

## 🪜 Plan par étapes
1. Hook `setZoomMix(zoom)` appelé dans la logique de zoom existante → courbe musique/
   ambiances. Test : zoomer/dézoomer au doigt, la bascule doit être imperceptible et belle.
2. Gain spatial dans le helper `play()` (calcul distance + rayon) → brancher d'abord UN
   émetteur (ouvrier qui récolte) et valider à l'oreille sur mobile.
3. Généraliser aux émetteurs du monde : ouvriers (récolte/plante/bulles), pompe/sprinklers,
   rivière (migrer son cas particulier vers le système commun), chantiers de construction.
4. Pan stéréo léger (option, désactivable si résultat bizarre sur haut-parleur mono).
5. Passe d'équilibrage finale avec Nano : rayon audible, courbes, cas du zoom max.

## ✅ Validation
En dézoomant, la musique enveloppe ; en zoomant sur un ouvrier, on l'entend travailler ;
un ouvrier à l'autre bout de la vallée est inaudible ; rien ne « saute ». **Effort : M**

---

# 🎬 MISSION 8 — Menu Principal & Menu Pause : la DA à l'extrême

## 🎯 Objectif
Créer l'**écran titre** et le **menu pause** les plus beaux possibles — 100% dans la DA
mystique/poétique + chill + fun décalé. C'est la première seconde du jeu : elle doit
donner le frisson et annoncer la qualité de toute l'expérience.

## 📍 État actuel dans le code & assets
- Le jeu **boote directement dans la vallée** : aucun écran titre, aucun menu pause.
- **Les 3 assets du menu sont dans `02_Asset/`** (uploadés le 05/07/2026) — specs vérifiées :
  · `Fond_1.png` — splash **« Cultivate Your Fortune! »** (lettrage or/violet magique),
    1536×1024, RGBA, **transparence propre** ✅, 0,84 Mo.
  · `Fond_2.png` — logo **« GROW ROOM »** (panneau bois, plantes, cristaux violets),
    1536×1024, palette+alpha ✅, 0,54 Mo.
  · `Fond_3.png` — **fond du menu principal** (salle au trésor gothique, plants sous
    lampe violette, or/lingots), 1672×941, opaque, 0,77 Mo.
- ⚠️ **Fond_3 est en paysage 16:9 pour un jeu portrait 9:16** → en plein écran mobile,
  seul ~1/3 de la largeur serait visible. Solution recommandée (voir Vision DA) : en
  faire une **dérive panoramique lente** (Ken Burns horizontal) — la contrainte devient
  une feature.
- ⚠️ **Poids intro ~2,15 Mo** → préchargement séquentiel obligatoire : `Fond_1` seul
  d'abord (affiché dès prêt), `Fond_2` puis `Fond_3` se chargent PENDANT le premier
  fondu. Les fondus masquent le chargement, le boot reste instantané.
- Les overlays HTML au-dessus du canvas sont le pattern maison (panneaux, toasts, cinés).
- ⚠️ **Pas de blur CSS sur le canvas** pour l'assombrissement du pause : un filtre de flou
  a déjà été retiré du code pour raisons de perf (ligne ~1253) → voile sombre + vignette,
  pas de blur.
- 🔗 **Synergie audio en or** : le tap sur le bouton « Jouer » du titre est LE geste
  utilisateur parfait pour débloquer l'AudioContext Android (contrainte n°1 de
  `AUDIO_HANDOFF.md`) — la musique naît exactement au moment où le joueur entre.

## 🎨 Vision DA — la séquence décidée par Nano
**Séquence d'ouverture (à chaque lancement) :**
1. **Écran sombre** (dégradé noir → violet très profond, raccord avec la DA des images).
2. **Fondu entrant** de `Fond_1` — « Cultivate Your Fortune! » — tenue ~1,8 s avec un
   très léger scale-up (1.00 → 1.04) + scintillement subtil des étoiles (opacité d'un
   calque de sparkles CSS), puis fondu sortant.
3. **Fondu entrant** de `Fond_2` — le logo « GROW ROOM » — même respiration, tenue un
   poil plus longue (~2,2 s, c'est LE logo), micro-balancement de vent optionnel.
4. **Fondu croisé** vers le **Menu Principal** : `Fond_3` plein écran en **dérive
   panoramique très lente** (Ken Burns horizontal gauche→droite, ~40 s aller-retour,
   easing doux) — la salle au trésor se découvre en continu, jamais figée.
   Par-dessus : logo `Fond_2` réduit en haut, **lucioles/particules violettes** qui
   flottent (canvas léger, ~15 particules), vignette sombre sur les bords.
5. Bouton unique **« 🌱 Cultiver »** (pulsation douce, dans les ors/violets de la DA).
   Dessous, discret : version + « Nano Studio ».
6. Au tap : **unlock audio** + fondu vers le jeu (option classe : enchaîner sur un
   `glideCam` d'arrivée sur la ferme).
- Un tap n'importe où pendant les splashs 1-2 les **skippe** (respect du joueur pressé).

**Menu Pause (bouton ⏸️ en jeu) :**
- Voile sombre + vignette sur le jeu (qui continue de vivre derrière, à peine visible).
- Panneau central façon **parchemin/bois** de la DA, entrée avec léger rebond : Reprendre ·
  Réglages (→ panneau M6) · Mon Domaine · Menu principal.
- Micro-détails décalés : une luciole qui se pose sur le coin du panneau, le titre du
  panneau qui ondule au vent.
- Sons : tout existe déjà dans le pack (`ui_panel_open/close`, `ui_btn`, `mus_menu_home`
  en option sur le titre).

## ✅ Décisions tranchées (critère : le plus beau)
1. **Logo** : `Fond_2.png` est le logo officiel.
2. **Dérive Ken Burns sur `Fond_3` : OUI** — panoramique gauche↔droite, aller-retour
   ~40 s, amplitude ~12% de la largeur, easing sinusoïdal (jamais de rebond sec aux
   extrémités). Le fond ne doit JAMAIS être figé.
3. **Timings de l'intro (la partition exacte)** :
   noir 0,4 s → fondu entrant `Fond_1` 0,8 s → tenue 2,0 s (scale 1.00→1.04 continu)
   → fondu sortant 0,7 s → fondu entrant `Fond_2` 0,8 s → tenue 2,4 s (même respiration)
   → **fondu croisé 1,2 s** vers le menu, avec entrée en cascade des éléments :
   `Fond_3` d'abord, puis le logo réduit (+150 ms), puis le bouton Cultiver (+150 ms) —
   la cascade, c'est ce qui fait premium. Total ~8 s, **skip au tap à tout instant**.
4. **Le pause NE fige PAS le temps** — c'est un idle, la vallée continue de vivre
   derrière le voile, et c'est beau à voir.

## 🪜 Plan par étapes
1. **Assets en place** : Nano upload `Fond_1/2/3.png` dans `02_Asset/` → le CLI vérifie
   chemins + rendu des transparences sur fond sombre.
2. **Séquence de splashs** : écran sombre → fondu `Fond_1` → fondu `Fond_2`, avec
   préchargement séquentiel masqué + skip au tap → capture de chaque étape, validation
   des timings avec Nano.
3. **Menu principal** : `Fond_3` en dérive Ken Burns + vignette + logo réduit + bouton
   « 🌱 Cultiver » pulsant + version/crédit → validation visuelle (portrait 390×844).
4. **Particules lucioles** par-dessus le fond (léger, ~15 max) + micro-polish.
5. **Entrée en jeu** : tap Cultiver → unlock audio + fondu (option glideCam d'arrivée).
6. **Menu pause** : voile + panneau DA + boutons branchés (Reprendre / Réglages M6 /
   Mon Domaine / Menu principal), entrée animée.
7. **Passage au crible mobile** : perf de la dérive + particules, mémoire (décharger les
   splashs après l'intro), test WebView Android.

## ✅ Validation
La première seconde donne envie de faire une capture d'écran ; la transition vers le jeu
est fluide sur mobile ; le pause est beau, lisible, et on en sort en un tap. **Effort : M/L**

---

## 📦 Livraison de chaque mission
Fin de sprint : captures Playwright avant/après · save rétro-compatible testée ·
`GAME_BIBLE.md` mis à jour (section concernée) · **tableau de suivi de CE doc mis à
jour (✅ + date + note)** · commit + push GitHub Pages · ligne de changelog dans
`CLAUDE.md`.

*Rédigé par Archi (sondage code v22 du 05/07/2026) — Nano Studio, TINY GROW.*
