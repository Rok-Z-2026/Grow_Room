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
Le système d'achat/évolution (payer pour passer au niveau suivant + bonus par niveau) est le
prochain chantier gameplay.

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

- **👷 Employés** — automatisent plantation, arrosage et récolte. Le pilier de l'idle.
- **🎯 Missions / Objectifs** — quêtes avec récompenses, donnent un but à court terme et guident la progression.
- **😴 Gains hors-ligne (Idle)** — la ferme produit pendant l'absence du joueur ; il encaisse à son retour.
- **🧪 Croisement de variétés (Labo)** — créer de nouvelles souches en croisant les existantes.
- **🎲 Mini-jeux** — ex. la *Fontaine de Sève* (et autres), pour varier le rythme et offrir des récompenses.
- **💾 Sauvegarde auto (localStorage)** — la partie se sauvegarde toute seule.
- **🌸 Prestige / Rebirth** — repartir à zéro contre des bonus permanents (talents Canabawa), pour relancer la boucle plus fort.

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
  jamais estompée (système d'achat/évolution : à brancher).
- Rendu : clip losange, eau animée 4 frames, effet vent sur la végétation, ombres (les ombres des
  arbres fondent avec leur arbre au zoom).
- Champs : terre labourée à sillons (`parc1..4`), touffes de 5 plants/case centrées, lanternes aux
  coins des parcelles owned ; **parcelles bonus de palier** (`PALIERS`, débloquées aux grammes
  totaux récoltés — `totalHarvest` — puis achetées en 💰 ; prochaine parcelle affichée en
  pointillés avec l'objectif "🔓 +X g").
- Système de plantes (6 variétés × 8 stades), marché fluctuant, soins (eau/soleil/sérum + combo +
  qualité), labo (rendement/vitesse/valeur), sauvegarde auto + offline capé 8h.

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
