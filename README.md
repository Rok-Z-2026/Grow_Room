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
- **Format** : 100 % client, un seul fichier `grow_world.html` (moteur + assets embarqués)

---

## 📁 Structure du dépôt

```
Grow_Room/
├── 01_Code/
│   └── grow_world.html  # Le jeu complet (moteur iso + PACK base64 embarqué) — ~17,7 Mo
├── 02_Asset/            # Sources des assets : atlas Glow_* (Git LFS), spritesheets
├── README.md            # Ce fichier
├── CLAUDE.md            # Contexte technique du moteur (pour Claude Code / contributeurs)
├── .nojekyll            # Désactive Jekyll → GitHub Pages sert les fichiers bruts
├── .gitattributes       # grow_world.html = git normal (Pages) / atlas Glow_* = Git LFS
└── .gitignore
```

> ℹ️ `grow_world.html` est volumineux car les assets (atlas/sprites) y sont
> embarqués pour rester en single-file portable. Voir la note versioning plus bas.

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

- `grow_world.html` est volontairement **hors Git LFS** : GitHub Pages ne sert pas
  correctement les fichiers LFS.
- Le fichier `.nojekyll` à la racine garantit que Pages sert les fichiers bruts
  (sans traitement Jekyll).
- Les atlas sources `Glow_*` restent en LFS (stockage dev), **non** servis par Pages.

---

## 🛠️ Développement

- Le moteur isométrique et la logique de jeu sont décrits dans **`CLAUDE.md`**.
- Les sources d'assets (atlas, tilesets) vivent dans **`02_Asset/`** ; le code et
  les outils dans **`01_Code/`**.

---

## 📦 Note versioning (gros fichiers)

- **`grow_world.html` (~17,7 Mo)** : versionné en **git normal** (pas en LFS) pour
  être servi tel quel par GitHub Pages. Sous la limite GitHub (avertissement à 50 Mo,
  blocage à 100 Mo), donc il passe.
- **Atlas sources `Glow_*` / spritesheets** (dans `02_Asset/`) : suivis via **Git LFS**
  (stockage dev, non servis par Pages). Voir `.gitattributes`.

> ⚠️ L'upload via l'interface web de GitHub **n'applique pas** le filtre LFS : pour
> ajouter les atlas en LFS, passer par `git` en ligne de commande (PC), pas par le web.
