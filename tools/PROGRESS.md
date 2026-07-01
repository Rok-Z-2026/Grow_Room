# TINY GROW — Progression intégration atlas (handoff)

> Note pour reprendre le travail dans une nouvelle session. Le site live :
> `https://rok-z-2026.github.io/Grow_Room/01_Code/grow_world.html`
> ⚠️ **Archi externalisée** : le PACK base64 (~30 Mo) est sorti du HTML en 170 PNG dans
> `02_Asset/runtime/`. Le HTML fait ~88 Ko. Voir `tools/README.md` pour le pipeline à jour.

## ✅ Déjà fait (live sur main)

### Plantes — `Glow_Plante.png` (grille 8 col × 6 lignes, cellule 384×435)
- 6 variétés = blocs **2×4** (4 stades en haut s1-4, 4 en bas s5-8). Mapping atlas→clé moteur :
  `v←V6 (vert)`, `p←V4 (violet)`, `b←V3 (bleu)`, `o←V2 (orange)`, `n←V1 (noir)`, `a←V5 (automne)`
  (V1=haut-gauche, V2=haut-droite, V3=mid-gauche, V4=mid-droite, V5=bas-gauche, V6=bas-droite).
- Clés PACK : `plant_{v,p,b,o,n,a}_{1..8}` (48). Moteur : `['v','p','b','o','n','a'][c.variety]`.
- **Rendu validé** = 4 plantes/case (taille adaptée au monde), recentrées :
  `for([0.30,0.30],[0.70,0.30],[0.30,0.70],[0.70,0.70]] -> sy=isoY(..)+TH()*0.12, scale TW*(0.28+0.20*(st/8))`
- Seedbar : 6 boutons (Verte/Violette/Bleue/Orange/Noire/Automne) + `flex-wrap`.

### Terrain Lot 1 — `Glow_Terrain.png` (grille **8×8**, cellule **512×512**, fond transparent)
Re-skin de 30 décors (PACK inchangé). Mapping FAIT :
- `bush1-6`   ← R0C0, R0C3, R0C4, R0C6, R1C2, R0C1
- `bushF1-6`  ← R0C2, R0C5, R1C0, R1C1, R1C3, R0C7
- `flower1-6` ← R4C5, R4C6, R4C7, R5C0, R5C1, R5C2
- `rock1-6`   ← R1C4, R1C5, R1C6, R1C7, R2C0, R2C1
- `stump1-6`  ← R2C2, R2C3, R4C2, R2C4, R2C7, R4C3

## 🗺️ Glow_Terrain — carte complète des 64 cases (R{ligne}C{colonne})
- **R0** buissons : C0 vert clair · C1 baies rouges · C2 fleuri jaune · C3 conifère · C4 fougère · C5 fleuri violet · C6 vert tondu · C7 baies orangées
- **R1** : C0 fleuri bleu · C1 fleuri rose · C2 herbe haute · C3 fleuri blanc · C4 rocher seul · C5 groupe rochers · C6 gros rocher fendu · C7 rocher moussu
- **R2** : C0 boulder pâle · C1 amas galets · C2 souche sciée · C3 souche+racines · C4 tas rondins · C5 rocher moussu · **C6 CHAMPIGNONS amanites** · C7 tronc creux
- **R3** eau/rochers : C0 amas rochers · C1 mare · C2 cascade · C3 terre rase · C4 étang nénuphars · C5 cascade · C6 étang nénuphars · C7 monticule+fleurs bleues
- **R4** : C0 feuilles automne · C1 fagots · C2 souche fleurie · C3 grume couchée · **C4 CLÔTURE bois** · C5 parterre mauve · C6 parterre jaune · C7 parterre violet
- **R5** : C0 fleurs blanc/rose · C1 marguerites · C2 fleurs bleu · **C3 sol gravier · C4 sol terre ocre · C5 sol pavé gris · C6 sol sable · C7 sol gazon**
- **R6** : **C0 CLÔTURE pierre · C1 CLÔTURE bois clair · C2 CLÔTURE pierre/bois** · C3 sol boue labourée · C4 sol terre humide · C5 sol paillis · C6 sol terre rouge · C7 sol galets
- **R7** sols : C0 gris-beige · C1 brun-sombre · C2 sable ocre · C3 dalle pierre · C4 gravier brun · C5 terre jaune-ocre · C6 herbe/mousse · C7 VIDE

## ⏳ À faire (lots suivants)

### Lot 2 — Sols (`sq_*`) — mapping PROPOSÉ (script `inject_terrain_sols.py` prêt, NON lancé)
Clés moteur (10) : `sq_grass, sq_moss, sq_dirt, sq_gravel, sq_mud, sq_path, sq_sand, sq_soil, sq_stone, sq_pond`.
Proposé : `sq_grass←R5C7, sq_moss←R7C6, sq_dirt←R7C1, sq_gravel←R7C4, sq_mud←R6C3, sq_path←R7C3, sq_sand←R7C2, sq_soil←R7C5, sq_stone←R5C5` (sq_pond → lot eau).
⚠️ Les cellules sol sont des **tuiles iso** (≈70% transparent) → extraire en détourant le diamant. `tile()` les clippe au losange (ow=w*1.12). Sols = TOUTE la carte → **valider visuellement avant push**.

### Lot 3 — Eau & clôtures
- `pond_big`/`pond_mare` ← R3C4, R3C6 (étangs nénuphars), R3C1 (mare) · `cascade` ← R3C2, R3C5
- `fence` (4 clés, cadres losange à centre VIDE) ← R4C4, R6C0, R6C1, R6C2
- `sq_pond` ← texture d'eau (mare R3C1 ?)

### Lot 4 — Champignons 🍄
- R2C6 (amanites rouges) → **pas de clé moteur** : créer `mushroom`/`shroom` + déco + placement.

### Autres atlas (pas commencés)
- `Glow_Arbre.png` : 12 arbres → `tree1-6` / `treeC1-6`
- `Glow_Maison.png` : 20 bâtiments → `house*`, `serre*`, `cabin`, `atelier1`…
- `Grow_Water_1.png` : spritesheet eau 2×2 → `water_f0-3` (eau animée)

## 🔧 Pipeline technique (voir scripts tools/) — ARCHI EXTERNALISÉE
1. **Extraction** : crop cellule, nettoyage par composantes connexes 2D (`scipy.ndimage.label`, garder blobs ≥5-8% du plus gros → vire fragments voisins), puis trim alpha. → `asset_lib.extract_sprite`.
2. **Écriture PNG + enregistrement clé** : `asset_lib.register_key` écrit `02_Asset/runtime/<clé>.png` (blob normal, PAS LFS) et ajoute la clé au tableau `const PACK=[...]` du HTML ; puis `rebuild_manifest()` régénère `manifest.json`. **Plus jamais de base64 dans le HTML.** Vérifier avec `asset_lib.audit()` (PACK ⇄ manifest ⇄ fichiers).
3. **Test Playwright** : viewport 393×844, DPR2, is_mobile+has_touch. Le lancement par défaut cherche un Chromium récent absent → utiliser
   `executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"`.
   Pour forcer des plants/sols à l'écran : hook JS qui set `cropCells`/`W.ground` puis recadre la caméra.
   Servir en HTTP (`python3 -m http.server` racine) pour reproduire Pages (casse sensible, chemins relatifs).
4. **Limite contexte images** : si la session sature, analyser les images via un **subagent** (contexte vierge) ou repartir sur une session fraîche.

## 📦 Notes
- `grow_world.html` ≈ **88 Ko** (moteur seul). Les 170 sprites (~22 Mo) sont dans `02_Asset/runtime/`.
- Optim mobile future possible : downscaler les PNG runtime (~×0.4) ou re-packer en 3-4 atlas + coords JSON (réduit le nombre de requêtes ; refacto rendu → valider séparément).
- Moteur : `decImg` → clé décor = `type+v` (ex `bush1`). `groundKey(g)` → clé `sq_*`.
