# tools/ — pipeline d'assets TINY GROW (archi externalisée)

Depuis l'externalisation du PACK (~30 Mo base64 → **170 PNG dans `02_Asset/runtime/`**),
ces scripts découpent les atlas `Glow_*` et écrivent des **PNG runtime**, puis
enregistrent la clé (tableau `const PACK=[...]` du HTML + `manifest.json`).
On ne ré-embarque **jamais** de base64 dans le HTML.

## Workflow pour intégrer / re-skinner un asset

1. **Découper** depuis l'atlas → **PNG** dans `02_Asset/runtime/<clé>.png`.
2. **Enregistrer** la clé : tableau `const PACK=[...]` + `manifest.json`.
3. **Valider visuellement** (Playwright 393×844 DPR2) **avant** de committer (règle d'or #4).

Tous les chemins sont déduits automatiquement (repo-relatifs) — plus de chemins
`scratchpad` à rafistoler.

## Scripts

| Script | Rôle |
|---|---|
| `asset_lib.py` | Cœur du pipeline : `extract_sprite`, `save_runtime`, `add_keys_to_pack`, `register_key`, `rebuild_manifest`, `audit`. Importé par les autres. Lancé seul → affiche l'audit de cohérence. |
| `extract_plantes.py` | (Re)génère les 48 sprites `plant_*` depuis `Glow_Plante.png`. |
| `extract_terrain_decor.py` | (Re)génère 30 décors (`bush*`, `bushF*`, `flower*`, `rock*`, `stump*`) depuis `Glow_Terrain.png`. |
| `extract_terrain_sols.py` | (Re)génère les sols `sq_*` depuis `Glow_Terrain.png`. |
| `rebuild_manifest.py` | Régénère `manifest.json` depuis les PNG présents + audit de cohérence. |
| `playwright_screenshot.py` | Capture de test (hook : déverrouille les zones, plante les variétés, zoome). |

Chaque script d'extraction est en **dry-run par défaut** (preview des dimensions,
rien écrit). Ajouter `--write` pour appliquer :

```bash
python3 tools/extract_terrain_sols.py            # preview
python3 tools/extract_terrain_sols.py --write     # écrit les PNG + met à jour PACK/manifest
python3 tools/rebuild_manifest.py                 # vérifie la cohérence à tout moment
```

## Dépendances

`pip install numpy scipy pillow` (+ `playwright` pour les captures).

## Test / capture

- Chromium pré-installé : `executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"`.
- Viewport **393×844**, **DPR 2**, contexte `is_mobile` + `has_touch`.
- Servir en HTTP (`python3 -m http.server` depuis la racine) pour reproduire GitHub Pages
  fidèlement (casse sensible, chemins relatifs `../02_Asset/runtime/<clé>.png`).

Voir `PROGRESS.md` pour la carte complète des atlas et l'historique d'intégration.
