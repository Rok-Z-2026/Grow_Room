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
- Fichier de travail : **`01_Code/grow_world.html`** (~17,7 Mo, single-file HTML).

---

## 🏗️ Architecture du fichier

- **Tout** est dans un seul HTML. Le **dernier `<script>`** contient tout le moteur.
- **PACK base64** : ligne ~96, objet `const PACK = {"clé":"data:image..."}` — **154 assets**.
- `IMG{}` est rempli en bouclant sur `PACK`. Clés des sols via `groundKey()`.
- **Boucle de rendu** : `function draw()` en `requestAnimationFrame`, **tri de profondeur
  isométrique** par `d = x + y`.

---

## 🔒 Règles d'or (CRITIQUE — ne JAMAIS oublier)

1. **Clip losange** dans `tile()` :
   `ctx.save()` → path diamant `moveTo`/`lineTo` → `ctx.clip()` →
   `drawImage` avec `ow = w * 1.12` → `ctx.restore()`.
   **NE JAMAIS le perdre.**
2. Quand on modifie le **PACK base64**, **réinjecter SANS effacer les autres clés**
   (injection après `"const PACK={"`).
   ⚠️ Effacer silencieusement les autres packs = **bug récurrent**.
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
│   └── grow_world.html   # Le jeu complet (moteur iso + PACK base64 embarqué)
├── 02_Asset/             # Sources des assets (atlas Glow_*, spritesheets)
├── README.md
├── CLAUDE.md             # Ce fichier
├── .gitattributes        # Tracking Git LFS
└── .gitignore
```
