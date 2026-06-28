# 🌿 TINY GROW — Les Graines de l'Oubli
### Bible du jeu — Document de design maître

> Ce document décrit la **vision, l'univers et les systèmes** du jeu.
> Pour la partie technique (architecture du code, règles de dev), voir `CLAUDE.md`.
> Les deux documents sont complémentaires : la Bible dit *ce qu'on construit et pourquoi*, le CLAUDE.md dit *comment c'est codé*.

---

## 1. 🎯 Pitch

**TINY GROW** est un jeu mobile *idle / cultivation* où le joueur incarne un cultivateur solitaire qui démarre son business de beuh à partir de rien — un petit lopin de terre, quelques graines — et grimpe, parcelle après parcelle, jusqu'à bâtir l'empire le plus stylé de la vallée.

> *« Pars d'une graine et d'un bout de terre. Deviens une légende. »*

Le titre **"Les Graines de l'Oubli"** raconte cette ascension : on commence oublié de tous, dans son coin, et on s'élève jusqu'à la richesse folle.

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

- **Départ** : un petit lopin avec quelques cases, quelques graines. Modeste, mais on n'est pas dans la misère totale.
- **Milieu** : on étend la ferme, on débloque des variétés, on automatise, on optimise sa stratégie de vente.
- **Endgame — l'EMPIRE COMPLET** :
  - Débloquer **toute la vallée** (expansion maximale du terrain).
  - **Collectionner toutes les variétés rares** (y compris les hybrides légendaires du labo).
  - Devenir le **baron du beu** : richesse maximale.

Le but ultime, c'est de réunir les trois : le territoire, la collection, et la fortune.

---

## 9. 🗺️ État du projet (résumé)

**Déjà en place (moteur iso) :**
- Monde isométrique : vallée en terrasses, rivière, village, décor riche.
- Rendu : clip losange, eau animée 4 frames, effet vent sur la végétation, ombres.
- Système de plantes (variétés × stades), parcelles de culture, marché, soins, labo, prestige, missions, mini-jeu Fontaine de Sève, employés.

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
