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

| Couleur | Rôle (à finaliser) | Rareté |
|---|---|---|
| 🟢 Verte | Souche de base, commune | Commune |
| 🔵 Bleue | Intermédiaire | Peu commune |
| 🟠 Orange | Intermédiaire+ | Rare |
| 🟣 Violette | Premium | Rare |
| ⚫ Noire | Premium, haute valeur | Très rare |
| ✨ (6e variété) | À définir | Légendaire ? |

> Le nouvel atlas `Glow_Plante.png` fournit **6 variétés × 8 stades** de croissance (graine → bourgeon mûr).
> *(Le moteur câble actuellement 4 variétés — un TODO d'intégration consiste à passer de 4 à 6.)*

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

**Règle d'or : « tu sèmes, ils entretiennent. »** Un ouvrier récolte les plants mûrs et replante
la **même variété** au même endroit. Il ne sème jamais une case vide que le joueur n'a pas semée,
ne soigne pas (qualité 1 — soigner reste le geste du joueur), et **ne vend jamais** (le marché
appartient au joueur). Si le joueur récolte à la main la cible d'un ouvrier, la main gagne.

**Embauche** (panneau 👷, débloqué à la maison niv 2 — il faut les loger) :

| Slot | Coût 💰 | Maison requise |
|---|---|---|
| 1 | 800 | niv 2 — La Cabane |
| 2 | 4 000 | niv 3 — La Chaumière |
| 3 | 20 000 | niv 5 — La Ferme |
| 4 | 90 000 | niv 7 — La Maison de Maître |
| 5 | 350 000 | niv 9 — La Villa |
| 6 | 1 200 000 | niv 10 — Le Manoir |

**Upgrades** : 👟 Bonnes bottes (+12% marche, ×10) · 🧤 Gants experts (-8% temps d'action, ×10) ·
🏮 Lanternes (+5% d'efficacité hors-ligne, ×5).

**Hors-ligne** : les ouvriers travaillent pendant l'absence à **35%** d'efficacité (jusqu'à
**60%** avec les Lanternes), dans la limite du cap de la maison (`homeOfflineH()`). Simulation
analytique déterministe (`min(bras, champ) × temps × efficacité × 16,5 g`), sans double-compte
avec la pousse : au retour, toast « 👷 Tes ouvriers ont récolté X g ! ».

*Visuel : emoji 👷 canvas (ombre, balancement de marche) en attendant les sprites `worker_1..3`
— le moteur les chargera automatiquement dès qu'ils entreront au PACK via le pipeline `tools/`.*

---

## 7ter. 🎯 Missions & Objectifs ✅ *(implémenté)*

Le **fil rouge de James** : une chaîne séquentielle de **40 missions en 6 chapitres** qui raconte
son ascension et guide le joueur vers chaque système dans l'ordre naturel. **Une seule mission
active à la fois** : pilule-tracker permanente sous la topbar (progression live, dorée pulsée
quand c'est accompli), modal détail au tap (citation de James, barre, récompense), **claim
manuel** — réclamer est le geste plaisir, jamais d'auto-claim. Récompense créditée atomiquement.

Chapitres : **I — Le lopin hérité** (tuto gestes : planter, soigner, récolter, vendre, combo) ·
**II — L'artisan** (labo, variétés, Cabane, 1er ouvrier) · **III — La ferme** (montée maison/
ouvriers/labo, 1re clairière) · **IV — Le domaine** (expansion) · **V — Le baron** (gros caps) ·
**VI — La légende** (toute la vallée, 6 ouvriers, 400 kg, Domaine de Luxe 🏆).

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
- Rendu : clip losange, eau animée 4 frames, effet vent sur la végétation, ombres (les ombres des
  arbres fondent avec leur arbre au zoom).
- Champs : terre labourée à sillons (`parc1..4`), touffes de 5 plants/case centrées, lanternes aux
  coins des parcelles owned ; **parcelles bonus de palier** (`PALIERS`, débloquées aux grammes
  totaux récoltés — `totalHarvest` — puis achetées en 💰 ; prochaine parcelle affichée en
  pointillés avec l'objectif "🔓 +X g").
- Système de plantes (6 variétés × 8 stades), marché fluctuant, soins (eau/soleil/sérum + combo +
  qualité), labo (rendement/vitesse/valeur), sauvegarde auto + offline capé par la maison.
- **👷 Ouvriers** : embauche (6 slots liés au niveau de maison), travail visible sur la map
  (marche, récolte, replante même variété), 3 upgrades, gains hors-ligne analytiques — voir 7bis.
- **🎯 Missions** : chaîne de 40 missions en 6 chapitres (voix de James), tracker permanent,
  claim manuel atomique, rétro-compatible vieux saves — voir 7ter.

**Atlas sources à intégrer (`02_Asset/`) :**
- `Glow_Arbre.png` — 12 arbres premium.
- `Glow_Maison.png` — 20 bâtiments (maisons, serres).
- `Glow_Plante.png` — 6 variétés × 8 stades de cannabis.
- `Glow_Terrain.png` — déco (buissons, rochers, souches, étangs, fleurs, sols, clôtures).
- `Grow_Water_1.png` — spritesheet d'eau.

**Prochains chantiers :**
- Intégration des nouveaux atlas (priorité : les plantes cannabis).
- Polish visuel continu de la map.
- Câblage / équilibrage des systèmes de jeu (idle, employés, croisement, etc.).

---

*Document vivant — à enrichir au fil du développement.*
*Projet : Nano Studio (Suisse). Assistant dev : "Archi".*
