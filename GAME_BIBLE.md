# 🌿 TINY GROW — Les Graines de l'Oubli
### Bible du jeu — Document de design maître

> Ce document décrit la **vision, l'univers et les systèmes** du jeu.
> Pour la partie technique (architecture du code, règles de dev), voir `CLAUDE.md`.
> Les deux documents sont complémentaires : la Bible dit *ce qu'on construit et pourquoi*, le CLAUDE.md dit *comment c'est codé*.

---

## 1. 🎯 Pitch & Histoire

**TINY GROW** est un jeu mobile *idle / cultivation* où le joueur incarne **James Lucky**.

**L'histoire** : James vient de perdre ses parents. En héritage, il ne reste qu'une chose — **un petit
lopin de terre perdu au fond d'une vallée sauvage**. Pas de village, pas de voisins, pas d'argent :
juste la nature à perte de vue, une bâche pour dormir et quelques graines. C'est ici que tout
commence… et c'est ici que James va bâtir **son empire** — d'abord à la main, parcelle après
parcelle, puis avec des **ouvriers**, des **villages entiers** qui pousseront autour de son domaine.

> *« Pars d'une graine et d'un bout de terre. Deviens une légende. »*

Le titre **"Les Graines de l'Oubli"** raconte cette ascension : on commence orphelin et oublié de
tous, au milieu de nulle part, et on s'élève jusqu'à la richesse folle.

### La Maison de James — 11 niveaux d'évolution
Le cœur visuel de la progression : le **domaine de James évolue en 11 étapes** (assets
`Home_Level_1..11` → runtime `home_1..home_11`), chacune étant un **diorama complet** (maison +
terrain + dépendances). *(Noms indicatifs, à affiner.)*

| Niv | Nom | Ce qu'on voit |
|---|---|---|
| 1 | **Le Campement hérité** | Bâche rapiécée, feu de camp, seau, cagette — la misère totale |
| 2 | La Cabane | Premiers murs, un vrai toit |
| 3 | La Chaumière | Petite maison en dur, charme rustique |
| 4 | La Maisonnette | La ferme s'organise, dépendances |
| 5 | La Ferme | Grande bâtisse, atelier, potagers, tour de guet |
| 6 | La Grande Ferme | Extensions, dépendances multiples |
| 7 | La Maison de Maître | Étage, standing, beaux matériaux |
| 8 | La Demeure | Grande demeure aboutie |
| 9 | La Villa | Élégance, jardins soignés |
| 10 | Le Manoir | Prestige, grandes ailes |
| 11 | **Le Domaine de Luxe** | Villa moderne, piscine, garage — le sommet |

Règles : la maison est posée **au centre de la vallée** (`HOME_POS`), n'est **jamais estompée** par le
fondu de zoom (c'est le repère du joueur), et son niveau (`houseLevel`) est **sauvegardé**.

### « Mon Domaine » — le système d'évolution ✅ *(implémenté)*

La progression de la maison est une **expérience**, pas un simple bouton d'achat :

- **Galerie de collection plein écran** (bouton 🏠 sous le labo, ou badge « 🏠N » de la topbar) :
  carrousel des 11 cartes (diorama, nom, bonus unique, état ✅ Possédé / 💰 Achetable /
  🔒 Verrouillé en silhouette noire), barre de progression dorée X/11, footer des bonus cumulés.
- **Conditions doubles** pour passer au niveau suivant : un **coût 💰** ET des **grammes totaux
  récoltés 🌿** (`totalHarvest`) — la maison monte avec la carrière du grower, pas juste le
  portefeuille. La carte affiche la condition manquante en clair (« Encore X g à récolter »).
- **Cinématique de chantier** à l'achat : la caméra glisse vers la maison (`glideCam`, ~600ms,
  zoom 1.05) → **chantier** ~1,6s (nuage de poussière/copeaux + 🔨✨ en rythme) → **reveal**
  (swap du diorama, onde dorée + halo radial, flash blanc doux) → toast « 🏠 Niveau X — Nom ! ».

| Niv | Nom | Coût 💰 | Grammes 🌿 | Bonus unique (cumulatif) |
|---|---|---|---|---|
| 1 | Le Campement hérité | — | — | — (le point de départ) |
| 2 | La Cabane | 500 | 0 | **+2h** de gains hors-ligne (un vrai lit !) |
| 3 | La Chaumière | 1 500 | 300 | **+8%** prix de vente |
| 4 | La Maisonnette | 4 000 | 1 000 | **+5** de stock max de soins |
| 5 | La Ferme | 10 000 | 2 500 | **-10%** sur le prix des parcelles |
| 6 | La Grande Ferme | 25 000 | 6 000 | **+2h** hors-ligne |
| 7 | La Maison de Maître | 60 000 | 15 000 | **+10%** prix de vente |
| 8 | La Demeure | 140 000 | 35 000 | **+30%** régénération des soins |
| 9 | La Villa | 320 000 | 80 000 | **+12%** prix de vente |
| 10 | Le Manoir | 700 000 | 180 000 | **-20%** sur le labo |
| 11 | Le Domaine de Luxe | 1 500 000 | 400 000 | **+15% vente** et **+4h** hors-ligne 🏆 |

Au sommet : **+45% vente · 16h hors-ligne · +5 soins max · -10% parcelles · +30% régén · -20% labo.**
Côté moteur : table `HOUSE`, helpers `homeSellMult/homeOfflineH/homeCareBonus/homeZoneDiscount/`
`homeCareRegenMult/homeLabDiscount` branchés dans `sellAll`, `updateStock`, `load()` (cap offline,
8h de base), `careMax()`, `zoneCost()`, `regenCare()` et `labCost()`.

---

## 1bis. 🗺️ Le Monde & la Carte

Une **vallée sauvage de 88×88 cases** (iso 3/4), rivières émeraude, forêts d'automne, cerisiers.

- **Au lancement, 100% nature** : aucun village, aucun bâtiment (`clearWorldToNature()` retire tout
  le bâti au boot). Les anciennes esplanades sont comblées de végétation (`natureFill()`).
- **Le domaine de James est AU CENTRE** de la vallée (`HOME_POS`), parvis de terre + couronne fleurie
  + allées d'accès. La caméra s'ouvre dessus. Son lopin hérité est collé au sud-ouest.
- **Trois routes de terre traversent la vallée** (`buildRoads()`) : Nord-Sud, Ouest-Est et une piste
  diagonale — elles **se croisent près de chez James** (il est au carrefour du monde, tout un
  symbole pour le futur baron).
- **Le territoire s'achète** : parcelles de palier collées au champ (grammes récoltés → 💰),
  clairières à défricher plus loin (éloignées du centre par `relocateObstacles()`).
- **Plus tard** : les villages renaîtront ici — construits par James, peuplés par ses ouvriers.

---

## 2. 🎨 Ton & Ambiance

Un **mélange assumé de trois saveurs** :
- **Mystique & poétique** — l'esthétique "Mystic Nature", digital-painting, une vallée enchantée hors du temps.
- **Chill & relaxant** — un cosy farming game où l'on prend plaisir à voir sa ferme grandir et respirer (vent dans les arbres, eau qui ondule).
- **Fun & décalé** — un humour léger, du second degré, une vibe qui ne se prend pas trop au sérieux.

L'univers de vente assume ce **mélange avec humour** : ni full underground glauque, ni dispensaire aseptisé — un ton stylé et fun.

**Plateforme** : mobile, format portrait 9:16.

---

## 3. 🎮 Boucle de jeu (Gameplay Loop)

La boucle cœur :

```
   PLANTER  →  POUSSER  →  RÉCOLTER  →  VENDRE  →  AMÉLIORER  →  (recommencer, en plus grand)
```

Avec un **fort axe idle** : les plantes poussent toutes seules, et le joueur encaisse des **gains hors-ligne** à son retour.

### Évolution du gameplay : manuel → automatique
- **Au début** : tout est **manuel**. Le joueur tape pour planter, arroser, récolter. Il sent le grind du débutant, chaque récolte compte.
- **En grandissant** : il débloque l'**automatisation** (employés, outils). Il passe de "petit grower qui bosse à la main" à "boss qui gère son empire pendant que ça tourne".

Cette montée en puissance — de l'effort manuel vers l'automatisation — est le cœur de la progression.

---

## 4. 💰 Le Business — comment on gagne

Les **trois piliers** comptent, et le joueur choisit sa stratégie :

1. **Vendre vite** → du cash immédiat pour réinvestir.
2. **Affiner la qualité** → garder et soigner ses plants pour une meilleure qualité = plus de valeur à la vente.
3. **Jouer le marché** → les prix fluctuent ; gérer son stock et vendre au bon moment.

Un bon joueur jongle entre les trois selon le moment.

---

## 5. 🌱 Les Variétés

Chaque couleur de plante est une **souche unique**, avec son **nom, sa valeur et sa rareté**.

**Retune v22 ✅** — les 6 variétés sont cultivées, chacune avec sa durée et son rendement
(le choix devient un vrai arbitrage temps/valeur, affiché sur la barre de graines) :

| Couleur | Durée | Rendement | g/min | Prix 💰 | Rareté |
|---|---|---|---|---|---|
| 🟢 Verte | 1 min | 6 g | 6.0 — l'onboarding vif | **Gratuit** | Commun ★ |
| 🪻 Violette | 1 m 40 | 11 g | 6.6 | 8 | Commun ★ |
| 🫐 Bleue | 2 m 30 | 18 g | 7.2 | 18 | Rare ★★ |
| 🍊 Orange | 3 m 30 | 28 g | 8.0 | 38 | Rare ★★ |
| 🖤 Noire | 4 m 30 | 40 g | 8.9 | 65 | Épique ★★★ |
| 🍁 Automne | 5 m 30 | 55 g | 10.0 — la patience paie (+67 %) | 110 | Légendaire ★★★★ |

> ±20 % d'aléa à la récolte. Moins de récoltes/min = moins de drain de fertilité (v23).
> La variété **légendaire** sera une **7e** variété (Saisons de l'Oubli, v30) — les 6
> existantes sont déjà toutes plantables, les verrouiller rétroactivement casserait les saves.

**Graines payantes (M4/TINY 7 ✅)** — chaque variété a un **coût à la plantation** (dans `VAR.c`),
affiché sur la barre de graines (grisée + non-cliquable si pas assez 💰). **La Verte reste
GRATUITE à vie** : filet de sécurité absolu, jamais de blocage économique. Les **ouvriers paient**
aussi la graine qu'ils replantent (online ET offline) ; **fauché → l'ouvrier rétrograde en Verte
gratuite** (l'idle ne s'arrête jamais, `coin` ne passe jamais < 0 ; offline le coût est netté
contre les ventes du vendeur puis clampé ≥0). Les **raretés** (Commun → Rare → Épique →
Légendaire : cadre coloré + étoiles, `RARITY`) sont un **habillage pur** — aucun taux d'échec, les
« conditions de réussite » restent les soins (eau/soleil/sérum → qualité). Coûts calibrés par
`tools/sim_seedcost.js` : rendement NET (coin/min) **croissant monotone** du tier, aucune variété
dominée par la Verte gratuite, idle toujours net-positif. **Zéro champ de save ajouté** (coût dérivé
du code → rétro-compat totale). *(Inventaire de graines en lots + hybrides rares du labo = v2.)*

### Croisement (Labo)
Système à **deux niveaux** :
- **Débloquer** de nouvelles variétés en progressant.
- **Croiser** deux souches pour créer des **hybrides rares** — le hook "découverte" : tomber sur une souche légendaire en croisant les bonnes.

---

## 6. 💎 Monnaies

| Monnaie | Symbole | Usage |
|---|---|---|
| **Cash** | 💰 | Monnaie du quotidien : acheter des graines, du terrain, améliorer (labo, outils). |
| **Canabawa** | 🌸 | Monnaie de prestige : obtenue au rebirth, sert à débloquer des **talents permanents**. |

---

## 7. ⚙️ Systèmes du jeu

Tous ces systèmes font partie de la vision finale :

- **👷 Employés** — automatisent la récolte et la replante. Le pilier de l'idle. ✅ *(implémenté — voir 7bis)*
- **🎯 Missions / Objectifs** — quêtes avec récompenses, donnent un but à court terme et guident la progression. ✅ *(implémenté — voir 7ter)*
- **😴 Gains hors-ligne (Idle)** — la ferme produit pendant l'absence du joueur ; il encaisse à son retour.
- **🧪 Croisement de variétés (Labo)** — créer de nouvelles souches en croisant les existantes.
- **🎲 Mini-jeux** — ex. la *Fontaine de Sève* (et autres), pour varier le rythme et offrir des récompenses.
- **💾 Sauvegarde auto (localStorage)** — la partie se sauvegarde toute seule.
- **🌸 Prestige / Rebirth** — repartir à zéro contre des bonus permanents (talents Canabawa), pour relancer la boucle plus fort.

---

## 7bis. 👷 Les Ouvriers ✅ *(implémenté)*

James a maintenant un toit — il peut embaucher. Les ouvriers **sortent du domaine** (l'allée
sud-ouest) et travaillent les champs, visibles sur la map : ils marchent case par case, se
penchent pour récolter (✂️) et replanter (🌱).

**Règle d'or (v19) : « tu sèmes, ils entretiennent — et s'ILS font plus, c'est parce que TU
l'as décidé. »** Un ouvrier arrive **Récolteur** : il récolte les plants mûrs et replante la
**même variété** au même endroit, ne sème jamais une case vide que le joueur n'a pas semée.
Les métiers qui vont plus loin (soigner, vendre) n'existent que par **réassignation manuelle**
— assigner un métier, c'est consentir. Dans tous les cas : si le joueur touche la cible d'un
ouvrier, **la main gagne** ; et les compteurs de missions « gestes » (`stats.ha/se/ea`) restent
exclusivement ceux de la MAIN du joueur.

**Les 4 métiers (v19)** — réassignables à tout moment, gratuitement, depuis la carte de
l'ouvrier :

| Métier | Ce qu'il fait | Garde-fous |
|---|---|---|
| 👷 **Récolteur** | la base : récolte + replante même variété | comportement v18 intact |
| 🧑‍🌾 **Jardinier** | arrose/soigne les plants en pousse, **gratuitement** | ne touche JAMAIS au stock de soins du joueur ; qualité plafonnée à 2.0 (niv 5) < 2.5 joueur ; cooldown 8s/plant (ré-armé au load — anti-exploit F5) ; pas de boost de pousse |
| 🤠 **Vendeur** | guette le marché, vend par **petits lots** (150-350 g) quand le prix passe le seuil (8/10/12, toggle pause) | prix 85→95% du marché (+Étal, jamais >100%) ; ne touche jamais stats.se/ea. **Philosophie : il achète ton temps, pas des grammes** — hors comparaison de rendement |
| 👨‍💼 **Contremaître** | patrouille les champs owned (📣), aura **globale** +10→20% (+Sifflet) sur vitesse d'action et de marche des autres | un seul compte (le meilleur niveau) — le 2e est décoratif et l'UI le grise |

**Identités & vie (v19)** : chaque slot d'embauche a son personnage FIXE (déterministe, zéro
random au load) — Marcel 🥖, Brume 🌫️, Gégé 🎺, Vieux-Saule 🌿, Ginette ☕, Lueur ✨,
Raymond 🎣, Mémé Rose 🌹 — mix titis français / mystiques de la vallée, répliques contrastées
en bulles canvas (1 max à l'écran, rotation ~9s, zoom > 0.75). Quand il n'y a rien à faire :
**pause hobby** à SON coin de vallée (Raymond pêche la berge, Ginette café sur l'esplanade,
Brume s'évapore dans la prairie…) — interrompue en ≤2s dès qu'un plant mûrit : zéro production
sacrifiée, par construction (la pause ne part que de la branche « aucune cible »).

**XP & niveaux (v19)** : cycle récolte +2 XP · soin +1 · vente +10 · contremaître +1/5 cycles
boostés. Seuils cumulés 60/240/540/1200 (niv max 5), gain ×(1+15%/niv Manuel). Effets par
niveau : récolteur −5% temps d'action · jardinier +0.125 de cap qualité · vendeur +2.5 pts de
prix · contremaître +2.5 pts d'aura. XP hors-ligne au prorata du travail simulé, cap
300/ouvrier/session, tout en floor() (déterministe).

**Répartition sur les champs** *(v15)* : chaque ouvrier choisit d'abord un **champ** (le moins
occupé par ses collègues, puis le plus proche) et y reste tant qu'il produit (assignation
sticky) — les équipes se répartissent naturellement sur toute la vallée. Trajet lointain →
il **presse le pas** (×1,8 au-delà de 6 cases) : on les voit traverser les routes.

**Embauche** (panneau 👷, débloqué à la maison niv 2 — il faut les loger) :

| Slot | Coût 💰 | Maison requise |
|---|---|---|
| 1 | 800 | niv 2 — La Cabane |
| 2 | 4 000 | niv 3 — La Chaumière |
| 3 | 20 000 | niv 5 — La Ferme |
| 4 | 90 000 | niv 7 — La Maison de Maître |
| 5 | 350 000 | niv 9 — La Villa |
| 6 | 1 200 000 | niv 10 — Le Manoir |
| 7 | 3 500 000 | niv 10 + 🛏️ Dortoir |
| 8 | 9 000 000 | niv 11 + 🛏️ Dortoir niv 2 |

**Le Camp (v19)** — bâtiments d'équipe posés sur la carte (assets `cabin`/`atelier1` déjà au
PACK, positions fixes slot-safe : Dortoir (48,45) berge SE, Atelier (48,40) bord de route NE,
`placeCamp()` idempotente rejouée au boot/load/reveal, cinématique de chantier façon maison) :
- 🛏️ **Le Dortoir** : niv 1 = 600 000 (maison ≥ 8), niv 2 = 2 000 000 (maison ≥ 10) —
  +1 lit par niveau (`wkMax()=6+dorm`). Les slots ≥ 7 sortent du Dortoir au spawn.
- 🛠️ **L'Atelier** : 500 000 (maison ≥ 7) — débloque les upgrades tier 2.

**Upgrades** : 👟 Bonnes bottes (+12% marche, ×10) · 🧤 Gants experts (-8% temps d'action, ×10) ·
🏮 Lanternes (+5% d'efficacité hors-ligne, ×5). **Tier 2 (Atelier)** : 🌾 Fertilisant maison
(+8% apport jardinier, ×5) · 🧺 Étal couvert (+3% prix vendeur, ×5) · 📯 Sifflet en laiton
(+3% aura, ×5) · 📖 Manuel de l'ouvrier (+15% XP, ×5).

**Le marché vivant (v19)** : le prix ondule vers une cible sinusoïdale déterministe
(`9,5 + 4,5·sin(2πt/30 min)`, filtre 0,15/60 s → amplitude vécue ≈ ±2,75, prix ~[6,75 ; 12,25]).
Les seuils du vendeur sont de VRAIS choix : ≥8 ≈ 68 % du temps, ≥10 ≈ 43 %, ≥12 ≈ 14 % (rare
mais juteux). Les ventes (joueur ET vendeur) gardent leur nudge aléatoire ±1 par-dessus, clamp
[5 ; 14] inchangé.

**Hors-ligne (v19, décomposé par métier — 100% déterministe)** : récolteurs
`min(Σ bras, champ) × temps × efficacité (35→60%) × 16,5 g × qOff`, dans la limite du cap
maison. Jardiniers → `qOff` (couverture ~20 plants/jardinier, facteur 0,65 = LE levier
d'équilibrage anti-méta : `[r,r,r,g]` ≥ 95 % de `[r,r,r,r]` à niv 3 champ non saturé, et > 100 %
champ saturé — le « tous récolteurs avant de dormir » ne paie pas). Vendeur → vend `F×` la
**production offline uniquement** (jamais le stock pré-existant du joueur) au prix moyen fermé
`P` au-dessus du seuil (approximation ASSUMÉE et conservatrice : en ligne, le backlog se vend au
passage de la vague). Toasts au retour : récolte 👷 puis vente 🤠 séquencés.

*Visuel (v23.5 ✅) : les 40 spritesheets `wk_1..wk_40` remplacent les emoji — tenue par MÉTIER
(Récolteur terre · Jardinier vert · Vendeur rouge de marché · Contremaître distingué), pick
déterministe par identité (`wkSprN`), 4 directions + cycle de marche 3 frames, portraits sprite
dans le panneau Équipe. Fallback emoji 👷 conservé pendant le chargement. Les 8 planches grises
sont réservées aux CLIENTS (v25).*

**Évolution VISIBLE (M5/TINY 6 ✅)** : les cartes montrent l'effet RÉEL du niveau + le prochain
palier chiffré (« Niv 3 → récolte −10% de temps · reste 37 XP », dérivé des vraies formules via
`wkFxTxt`), les **carrières** par perso (🌿 g récoltés · 🧺 g vendus — comptées online ET
offline), et les synergies Camp pertinentes (📖/🌾/🧺/📯). Le **level-up se FÊTE** : bannière
dorée + `sfx_gauge_fill` (niv 2-4) ou 🏆 + `stg_worker_hired` + double burst (niv MAX) ; les
gains d'XP quotidiens s'affichent en « +N XP » flottants agrégés (throttle 2,5 s, visibles à
l'écran seulement). **Badge ⭐** bondissant sur le bouton 👷 à chaque promotion (persisté
`st.wkLu`, éteint à l'ouverture du panneau). **Rapport de fierté offline** : les promotions
d'absence sont fêtées au retour (bannières à 5,3 s ; ≥3 promus → bannière collective, un MAX
garde la sienne). **Les Dons (perks niv 5)** : au sommet, chaque perso révèle UN don choisi
parmi les 2 de son métier (double-tap de confirmation, irréversible) — 🥖 Bras de boulanger
(+8% grammes) / 🌬️ Pas de montagnard (−8% temps) · 🧚 Pouce de fée (+10% soin) / 🌙 Murmure
aux plantes (ré-armé −15%) · 🧺 Panier sans fond (lots +8%) / 🤝 Poignée de main d'or (prix
+2 pts DANS le cap ≤100%) · 📣 Voix de stentor (aura +2 pts) / 🎓 École du soir (+10% XP
équipe). Le don est lié à l'IDENTITÉ : réassigné → 💤 dormant (jamais reset). Save additive
`crew:[j,xp,pk,hg,sg]`, garde-fous v19 tous intacts (boosts{}, clamp gCap, vMult ≤1, qOff 0,65).

---

## 7ter. 🎯 Missions & Objectifs ✅ *(implémenté)*

Le **fil rouge de James** : une chaîne séquentielle de **53 missions en 8 chapitres** qui raconte
son ascension et guide le joueur vers chaque système dans l'ordre naturel. **Une seule mission
active à la fois** : carte-tracker permanente sous la topbar *(v15 : médaillon doré, barre
épaisse avec reflet animé, fraction ; accomplie → fond or, rayons tournants, 🎁 qui bounce)*,
modal détail au tap (citation de James, barre, récompense, bouton **📍 Montre-moi** qui guide
caméra/bouton vers l'objectif), **claim manuel** — réclamer est le geste plaisir, jamais
d'auto-claim. Au claim : pièces 💰 qui **volent vers le compteur** (count-up animé), bannières
d'événement « Mission accomplie ! » / « Nouvelle mission ». Récompense créditée atomiquement.

Chapitres : **I — Le lopin hérité** (tuto gestes : planter, soigner, récolter, vendre, combo) ·
**II — L'artisan** (labo, variétés, Cabane, 1er ouvrier) · **III — La ferme** (montée maison/
ouvriers/labo, 1re clairière) · **IV — Le domaine** (expansion) · **V — Le baron** (gros caps) ·
**VI — La légende** (toute la vallée, 6 ouvriers, 80 kg, Domaine de Luxe 🏆) ·
**VII — Le patron** *(v19 : Atelier, jardinier, vendeur, Dortoir, 7-8 ouvriers, un maître
niv 5)* · **VIII — L'Ingénieur** *(v22 : 1er module d'Irrigation, 8 champs couverts d'eau,
un module niv 2 ; +3 missions v23 : Table d'engrais, Générateur, Overdrive — append strict :
les indices existants sont gravés dans les saves)*.

---

## 7quater. 🏗️ Les Modules ✅ *(v22 — 1re tranche du GDD « L'Exploitation »)*

La vallée devient un **plan d'usine** : 6 familles de bâtiments de gestion à **placement
LIBRE** (30 assets, 5 niveaux chacun), portée en losange Manhattan (3/4/4/5/6), **pas
d'empilement** (deux modules identiques : seul le meilleur niveau compte par case), copies
multiples (prix ×1.5^copie, cap 2+⌊Domaine/3⌋). Menu 🏗️ dès le Domaine 3, ghost de pose avec
halo de couverture, cinématique de chantier, panneau au tap (effet actuel → suivant chiffré,
vue des portées 📡). Portes des niveaux 3/4/5 : **grammes de carrière** (1 600 / 8 000 /
25 000 — transitoire v22-v24, la réputation arrive en v25 avec GRANDFATHERING).

*UX machines (M2/TINY 6 ✅)* : les machines ne s'estompent **jamais** (opaques comme la
maison, mais restent cibles du fondu) · en mode pose, **cases vertes recommandées**
(dilatation inverse depuis les champs NON couverts — valeur ajoutée seulement, jamais de vert
mensonger) + hint à la 1re pose · le ghost affiche le **bénéfice concret vivant** (« 💧 +2
eau/min · pousse jusqu'à +4.5% sur 7 champs couverts » — % réel par niveau, dérivé de
`MODS_CFG`/`IR_SPD`) · **liseré bleu discret permanent** sur les champs couverts (couverture
ACTIVE via `cmAt` : recule honnêtement en pénurie ⚡) · panneau : « 📍 couvre X champs ·
pousse +Y% effectif » (moyenne d'`irSpd` réelle) · toast pédagogique à la toute première
construction (flags additifs `st.mHint`/`st.mFx`).

**💧 Irrigation (active)** : chaque champ a une jauge d'eau vivante (drain −1/min) ; le module
la remplit à portée (+2/+4/+6/+8/+12 par min, caps 60/80/100/120/140) ; **l'eau accélère la
pousse** (jusqu'à +15 %, +15 % constant sous le Hub Lv5) ; Sprinklers Lv4+ arrosent à la
plantation (joueur ET ouvriers). Offline : eau à l'équilibre, formule fermée déterministe.
Arrosoir → Pompe → Château d'eau → Sprinklers → Hub auto (800 → 600 k 💰).

**⚡ Énergie (v23 ✅)** : le réseau global — les modules Lv2+ consomment, les générateurs
produisent (10→400 ⚡), badge topbar dès le Domaine 5. Pénurie → mode DÉGRADÉ affiché (portée
÷2 + effets ×0.5 des Lv2+ ; les Lv1 artisanaux tiennent bon). **Overdrive** : +25% de vitesse
globale 10 min (réserve 150⚡, cooldown 1h, surplus ≥150 requis) — l'Energy Core Lv5 le
déclenche automatiquement. Modal « Le Réseau » au tap du badge.

**🌾 Nutriments (v23 ✅)** : la FERTILITÉ vit par case (60-140%, base 100) — chaque récolte
épuise (−5%), régén naturelle lente (plafond 85%), le module Nutriments régénère vers des caps
croissants (110→140%). La fertilité multiplie les grammes ; la terre change de teinte (brun
fatigué / vert riche). Offline 100% fermé et déterministe. La porte fert>100 → ★4+ arrive
avec la Qualité 2.0 (v24).

**📖 Carnet v1 (v23 ✅)** : James diagnostique sous le tracker — pénurie d'énergie, champs
sans irrigation, sol fatigué — avec le remède (🏗️). Hystérésis 5 min, « ✅ Réglé » quand tu
corriges. Missions 50-52 (chapitre VIII continue : Table d'engrais, Générateur, Overdrive).

**v23.5 « Les Visages de la Vallée »** ✅ : les sprites des Employés 2.0 (volet visuel de la
v27) ont été AVANCÉS — voir 7bis. Le reste du chantier v27 (assignation par champ, Technicien,
Centre des employés) garde sa place dans la roadmap.

**v24 🔊 « La Vallée qui chante »** ✅ : le jeu a une bande-son complète (88 MP3 ElevenLabs,
83 câblés). Boucle cœur (plante/soins/combos à pitch montant/récolte/vente), ambiance de la
vallée crossfadée + musique douce + **rivière/pompe/feu de camp spatialisés** (volume ∝
distance caméra), UI et toasts intelligents (zéro doublon), stingers de mission/reveal/embauche
avec **ducking**, ouvriers à −6dB seulement à l'écran, retour offline séquencé, rafales de
vent, grillons au dézoom, musique dédiée de la galerie du Domaine, toggle 🔊/🔇 persistant,
économie de batterie. Le son ne casse JAMAIS le jeu (panne = silence).

**À venir** (une tranche jouable par version) : ★ Qualité + 📦 Logistique (v24) ·
🛒 Commandes/Réputation (v25, les clients utiliseront les 8 planches grises) · 🌡️ Climat +
Événements (v26) · 👷 Employés 2.0 — suite (v27) · 📖 Carnet complet (v28) · équilibrage (v29) ·
🌸 Saisons de l'Oubli (v30). Le document de référence : le GDD approuvé « L'Exploitation »
(03_Design/GDD_EXPLOITATION.md).

Récompenses 💰 (50 → 250 000, total ≈ 908 000 ≈ 18 % des coûts endgame — coup de pouce, pas de
triche) + quelques recharges de soins. Objectifs dérivés de l'état (`totalHarvest`, `houseLevel`,
`workerCount`, zones/clairières, niveaux labo/upgrades) → **progression rétroactive** ; les
gestes (semis, soins, combo, ventes) sont comptés dans `stats{}` (persisté).

**Vieux saves** : stratégie « gestes tôt + preuve d'état » — les missions prouvables par l'état
se valident seules (un vétéran chain-claim ses récompenses en retard dans le modal), les gestes
non prouvables restent demandés mais minuscules (<1 min, tuto rejouable, jamais punitif).

---

## 8. 📈 Progression & Endgame

- **Départ — la misère totale** : James arrive sur le lopin hérité de ses parents. **Le monde est
  100% nature sauvage** (aucun village, aucun bâtiment) ; il n'a que son campement (maison niv 1),
  quelques pièces et des graines. Tout est manuel, chaque récolte compte.
- **Milieu** : on étend la ferme (parcelles de palier collées au champ), on débloque des variétés, on
  fait **évoluer la maison** (niv 2 → 8), on automatise, on optimise sa stratégie de vente.
- **Endgame — l'EMPIRE COMPLET** :
  - Débloquer **toute la vallée** (expansion maximale du terrain).
  - Maison au **niveau 11** (domaine de luxe).
  - **Des villages entiers** construits par James et peuplés de **ses ouvriers** (l'automatisation
    incarnée dans le monde : ce ne sont plus des menus, ce sont des gens qui bossent pour lui).
  - **Collectionner toutes les variétés rares** (y compris les hybrides légendaires du labo).
  - Devenir le **baron du beu** : richesse maximale.

Le but ultime, c'est de réunir les quatre : le territoire, le domaine, les hommes, et la fortune.

---

## 8bis. 🎬 L'Ouverture — Menu Principal & Pause ✅ *(M8/TINY 6)*

**La première seconde donne le frisson** : à chaque lancement, noir 0,4 s → fondu
« Cultivate Your Fortune! » (respiration scale 1,00→1,04) → logo « GROW ROOM » → fondu
croisé vers le **menu principal** : la salle au trésor (`Fond_3`) en **dérive Ken Burns**
(aller-retour 40 s, amplitude 12 %, jamais figée), vignette sombre, logo réduit,
15 **lucioles violettes** (GPU pur), bouton « 🌱 Cultiver » pulsant or/violet, crédit
« 🏮 v24 · Nano Studio ». **Skip au tap à tout instant** (la cascade d'entrée joue quand
même). Préchargement séquentiel : `Fond_1` part avant le storm des 256 PNG, `Fond_2/3` se
chargent sous le premier fondu. Splashs retirés du DOM après l'intro (mémoire).

**Le son naît avec le joueur** : le tap (skip ou Cultiver) débloque l'AudioContext →
`mus_menu_home` (téléchargée en priorité `p1`) enveloppe le titre ; une **porte dans
`sndAmbTick`** garantit que la vallée ne démarre JAMAIS sous le menu. Au tap Cultiver :
crossfade musique, **glideCam d'arrivée sur la ferme** (au boot uniquement), et la cascade
« bon retour » (toasts + stingers offline, différée via `_welcome`) se joue enfin
AUDIBLE — avant M8 elle partait sous le boot, muette.

**Menu pause** (⏸️ topbar) : voile + vignette (zéro blur canvas — interdit perf), panneau
bois DA avec entrée rebond et une luciole qui se pose sur son coin. Reprendre · ⚙️ Réglages ·
Mon Domaine · Menu principal (retour au titre SANS rejouer les splashs, la vallée continue
de vivre derrière — **le pause ne fige jamais le temps**, c'est un idle). Hook
debug/harnais : `#nointro` = boot direct.

**⚙️ Réglages (M6/TINY 6 ✅)** : sous-écran du pause. Mute global 🔊/🔇 + **4 sliders par
famille** (🎵 Musique · 🌿 Ambiances · ✨ Effets [sfx+stingers] · 🖱️ Interface), audibles
en direct (rampe 50 ms en glissant, blip témoin au relâcher), + toggle « 👷 Sons des
ouvriers » (couche wk dédiée). Persistance : clé `'tinygrow_sound'` en JSON rétro-compatible
(`{"on":1,"v":{mus,amb,fx,ui,wk}}` — les vieux `'1'/'0'` donnent on/off + défauts),
appliquée au boot. **Source unique `SND_VOL`/`sndVol(l)`** = constante de mixage × réglage
joueur : le ducking des stingers et le dim du menu titre restaurent le volume DU JOUEUR,
plus jamais la constante d'usine. **Zone danger** : « 🧨 Réinitialiser la partie » en
double-tap armé (« ✔ SÛR ? », désarmement 4 s) → purge save + réglages son, partie neuve.
À propos : 🌱 TINY GROW · 🏮 v24 · Nano Studio.

**📡 Mixage spatial (M7/TINY 6 ✅) — le son vit avec la caméra** : dézoomé au-dessus de la
vallée, la musique porte (×1,0) ; zoomé près du sol, elle s'efface (×0,35) et laisse la
place aux sons du monde (ambiances inverses ×0,7→×1,0, rampes 0,4 s — bascule
imperceptible). Les sons **positionnés** (ouvriers…) ont un gain graduel `1−(d/R)²` :
proche du centre = net, bord = discret, hors rayon = pas joué du tout (économie CPU) +
**pan stéréo léger** ±0,4 selon la position à l'écran (fallback mono propre). Jamais
spatialisés : les gestes du joueur, l'UI, les stingers, la musique. Les boucles
rivière/pompe/feu gardent leur spatialisation v24 dédiée (déjà graduée par distance).

---

## 9. 🗺️ État du projet (résumé)

**Déjà en place (moteur iso) :**
- **Monde** : vallée 88×88 remise à l'état **100% nature** au boot ; **maison de James au centre**
  (parvis + couronne fleurie + allées) ; **3 routes de terre** qui traversent et se croisent au
  centre ; trous des ex-villages comblés de végétation ; clairières éloignées du domaine.
  (Pipeline : `relocateStarter` → `relocateObstacles` → `initBonusZones` → `clearWorldToNature` →
  `buildRoads` → `natureFill` → `placeHome` — voir CLAUDE.md.)
- **Maison de James** : 11 dioramas (`home_1..home_11`) intégrés ; `houseLevel` sauvegardé ;
  jamais estompée. **Système « Mon Domaine » branché** : galerie de collection plein écran,
  conditions doubles (💰 + grammes totaux), bonus uniques cumulatifs par niveau, cinématique de
  chantier à l'achat (caméra + poussière + reveal doré) — voir section 1.
- Rendu : clip losange, **eau VIVANTE (M1/TINY 6 ✅ — fake shader : 10 frames générées au
  boot depuis `Water_Dif_2` déformée par sa normal map, boucle parfaite, grading émeraude ;
  l'eau ondule même caméra immobile ; fallback 4 frames v24 à vie)**, effet vent sur la végétation, ombres (les ombres des
  arbres fondent avec leur arbre au zoom).
- Champs : terre labourée à sillons (`parc1..4`), touffes de 5 plants/case centrées, lanternes aux
  coins des parcelles owned ; **parcelles bonus de palier** (`PALIERS`, débloquées aux grammes
  totaux récoltés — `totalHarvest` — puis achetées en 💰 ; prochaine parcelle affichée en
  pointillés avec l'objectif "🔓 +X g").
- Système de plantes (6 variétés × 8 stades), marché fluctuant, soins (eau/soleil/sérum + combo +
  qualité), labo (rendement/vitesse/valeur), sauvegarde auto + offline capé par la maison.
- **👷 Ouvriers v19** : 8 slots (6 + Dortoir), 4 métiers réassignables (récolteur/jardinier/
  vendeur/contremaître), identités fixes + XP/niveaux, Camp (Dortoir/Atelier + upgrades T2),
  marché sinusoïdal vivant, pauses hobby, offline par métier — voir 7bis.
- **🎯 Missions** : chaîne de 53 missions en 8 chapitres (voix de James), tracker permanent,
  claim manuel atomique, rétro-compatible vieux saves — voir 7ter.
- **🏗️ Modules v22** : 6 familles à placement libre (💧🌾⚡ achetables), portées Manhattan,
  💧 Irrigation active — voir 7quater.
- **⚡🌾 Réseau & Terre v23** : énergie (production/consommation, pénurie, Overdrive) +
  fertilité par case + Carnet v1 (diagnostic une ligne) — voir 7quater.
- **👷 Employés 2.0 visuel v23.5** : 40 spritesheets `wk_1..wk_40` remplacent les emoji —
  voir 7bis.
- **🔊 Audio v24** : bande-son complète Web Audio (83/88 MP3 câblés, ambiances spatialisées,
  stingers, ducking) — « La Vallée qui chante ».

**Atlas sources (`02_Asset/` — intégrés ✅, conservés comme archives dev) :**
- `Glow_Plante.png` ✅ (48 sprites `plant_*`) · `Glow_Terrain.png` ✅ lot 1 (30 décors).
- `Glow_Arbre.png` / `Glow_Maison.png` / `Grow_Water_1.png` — réserves non découpées
  (le moteur a déjà arbres/bâtiments/eau runtime ; à puiser au besoin).
- Nouveaux (05/07/2026) : `Fond_1/2/3.png` (menus M8) · `Water_Dif/NRM_1/2.jpg` (eau M1).

**Prochains chantiers :**
- **TINY 6** (`ROADMAP_MISSIONS.md`) : M2 🔵 en cours, puis M5 → M8 → M6 → M7 → M1 → M4 → M3.
- Ensuite, reprise de l'arc GDD « L'Exploitation » : ★ Qualité 2.0 + 📦 Logistique,
  🛒 Commandes/Réputation, 🌡️ Climat, 📖 Carnet complet, 🌸 Saisons de l'Oubli.

---

*Document vivant — à enrichir au fil du développement.*
*Projet : Nano Studio (Suisse). Assistant dev : "Archi".*
