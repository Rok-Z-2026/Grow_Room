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
  "../02_Asset/runtime/"`. **185 assets**, chacun un PNG dans `02_Asset/runtime/<clé>.png`
  (dont `home_1..home_11` : les 11 niveaux du domaine de James, dioramas complets).
- `IMG{}` est rempli en bouclant sur `PACK` : `im.src = ASSET_BASE + k + ".png"`.
  Clés des sols via `groundKey()`.
- **Manifest** : `02_Asset/runtime/manifest.json` liste les 185 clés (source de vérité).
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
- **Eau animée** 4 frames (`water_f0`–`water_f3`) ✓
- **Vent** (`drawSpWind`) ✓
- **Ombres** (`function shadow`) ✓
- **Plantes** : 4 variétés (`v` / `p` / `b` / `o`) × 8 stades → `plant_X_1` à `plant_X_8`
- **Décor** : trees, bushes, flowers, rocks, stumps, bâtiments, rampes, plans d'eau

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
