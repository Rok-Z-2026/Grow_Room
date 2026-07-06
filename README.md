# 🌱 TINY GROW — Les Graines de l'Oubli

Jeu **idle** de culture de cannabis dans un **monde isométrique**, livré sous
forme d'un **unique fichier HTML** autonome (single-file). Aucune installation,
aucun serveur : on double-clique, ça tourne dans le navigateur.

---

## 🎮 Le jeu

- **Genre** : idle / gestion, progression passive
- **Univers** : monde isométrique 3/4 (style *Hay Day* / *Township*), esthétique « Mystic Nature »
- **Thème** : culture de cannabis stylisée, montée en puissance d'une grow room
- **Cible** : mobile portrait 9:16
- **Format** : 100 % client — moteur dans `grow_world.html` (~88 Ko), assets servis depuis `02_Asset/runtime/`

---

## 📁 Structure du dépôt

```
Grow_Room/
├── 01_Code/
│   └── grow_world.html  # Le moteur iso (~88 Ko) — charge les assets externes
├── 02_Asset/            # Atlas sources Glow_* (Git LFS, dev), spritesheets
│   └── runtime/         # 170 PNG servis au jeu (blobs normaux, PAS LFS) + manifest.json
├── README.md            # Ce fichier
├── CLAUDE.md            # Contexte technique du moteur (pour Claude Code / contributeurs)
├── .nojekyll            # Désactive Jekyll → GitHub Pages sert les fichiers bruts
├── .gitattributes       # grow_world.html + runtime/ = git normal (Pages) / atlas Glow_* = Git LFS
└── .gitignore
```

> ℹ️ Le moteur `grow_world.html` est léger (~88 Ko) : les 170 assets ont été
> **externalisés** dans `02_Asset/runtime/` (PNG raw, chargés par chemin relatif).
> Objectif : workflow git/remote rapide + chargement Pages optimisé. Voir la note
> versioning plus bas.

---

## ▶️ Lancer le jeu

Aucune dépendance, aucun build nécessaire pour jouer :

1. Récupérer le dépôt (clone ou téléchargement ZIP).
2. Ouvrir **`01_Code/grow_world.html`** dans un navigateur récent (Chrome / Firefox / Edge).
3. C'est tout — le jeu démarre.

> 💡 Si une fonctionnalité nécessite un contexte sécurisé (stockage, workers…),
> servir le dossier en local plutôt que d'ouvrir le fichier via `file://` :
> ```bash
> # depuis la racine du dépôt
> python3 -m http.server 8080
> # puis ouvrir http://localhost:8080/01_Code/grow_world.html
> ```

---

## 🌐 Jouer en ligne (GitHub Pages)

Le jeu est déployé via **GitHub Pages** (branche `main`, dossier racine) :

**▶️ https://rok-z-2026.github.io/Grow_Room/01_Code/grow_world.html**

- `grow_world.html` **et** les PNG de `02_Asset/runtime/` sont volontairement **hors Git LFS** :
  GitHub Pages ne sert pas correctement les fichiers LFS. Ce sont des blobs git normaux.
- Le fichier `.nojekyll` à la racine garantit que Pages sert les fichiers bruts
  (sans traitement Jekyll).
- Les atlas sources `Glow_*` restent en LFS (stockage dev), **non** servis par Pages.

> ⚠️ **Déploiement** : Pages sert la branche **`main`**. Les changements sur une branche
> de feature ne sont visibles en ligne **qu'après merge sur `main`**.

---

## 🛠️ Développement

- Le moteur isométrique et la logique de jeu sont décrits dans **`CLAUDE.md`**.
- Les sources d'assets (atlas, tilesets) vivent dans **`02_Asset/`** ; le code et
  les outils dans **`01_Code/`**.

---

## 📦 Note versioning (gros fichiers)

- **`grow_world.html` (~88 Ko)** : moteur seul, versionné en **git normal** (pas en LFS),
  servi tel quel par GitHub Pages. Léger → chaque commit de code est minuscule.
- **`02_Asset/runtime/` (170 PNG, ~22 Mo au total)** : assets du jeu, versionnés en
  **git normal** (pas en LFS, pour Pages). Ne changent que si un asset change → pas de
  churn sur le workflow de code.
- **Atlas sources `Glow_*` / spritesheets** (dans `02_Asset/`) : suivis via **Git LFS**
  (stockage dev, non servis par Pages). Voir `.gitattributes`.

> ⚠️ L'upload via l'interface web de GitHub **n'applique pas** le filtre LFS : pour
> ajouter les atlas en LFS, passer par `git` en ligne de commande (PC), pas par le web.

> 🚀 Déployé : v24 + TINY 6 (M2 machines · M5 employés · M8 ouverture · M6 réglages · M7 spatial) — 2026-07-06 (relance n°3).
