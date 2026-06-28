# 🌱 TINY GROW — Les Graines de l'Oubli

Jeu **idle** de culture de cannabis dans un **monde isométrique**, livré sous
forme d'un **unique fichier HTML** autonome (single-file). Aucune installation,
aucun serveur : on double-clique, ça tourne dans le navigateur.

---

## 🎮 Le jeu

- **Genre** : idle / gestion, progression passive
- **Univers** : monde isométrique, ambiance contemplative (« Les Graines de l'Oubli »)
- **Thème** : culture de cannabis, montée en puissance d'une grow room
- **Format** : 100 % client, un seul fichier `grow_world.html` (moteur + assets embarqués)

---

## 📁 Structure du dépôt

```
Grow_Room/
├── grow_world.html      # Le jeu complet (moteur iso + assets embarqués) — ~17,7 Mo
├── 01_Code/             # Sources du moteur, scripts, outils de build
├── 02_Asset/            # Sources des assets : atlas, sprites, tilesets isométriques
├── README.md            # Ce fichier
├── CLAUDE.md            # Contexte technique du moteur (pour Claude Code / contributeurs)
└── .gitignore
```

> ℹ️ `grow_world.html` est volumineux car les assets (atlas/sprites) y sont
> embarqués pour rester en single-file portable. Voir la note Git LFS plus bas.

---

## ▶️ Lancer le jeu

Aucune dépendance, aucun build nécessaire pour jouer :

1. Récupérer le dépôt (clone ou téléchargement ZIP).
2. Ouvrir **`grow_world.html`** dans un navigateur récent (Chrome / Firefox / Edge).
3. C'est tout — le jeu démarre.

> 💡 Si une fonctionnalité nécessite un contexte sécurisé (stockage, workers…),
> servir le dossier en local plutôt que d'ouvrir le fichier via `file://` :
> ```bash
> # depuis la racine du dépôt
> python3 -m http.server 8080
> # puis ouvrir http://localhost:8080/grow_world.html
> ```

---

## 🛠️ Développement

- Le moteur isométrique et la logique de jeu sont décrits dans **`CLAUDE.md`**.
- Les sources d'assets (atlas, tilesets) vivent dans **`02_Asset/`** ; le code et
  les outils dans **`01_Code/`**.

---

## 📦 Note versioning (gros fichiers)

`grow_world.html` pèse ~17,7 Mo. C'est sous la limite GitHub (blocage à 100 Mo,
avertissement à 50 Mo), donc il passe — mais c'est lourd à versionner si le fichier
change souvent. Selon le choix retenu, le dépôt peut utiliser **Git LFS** pour les
gros binaires (voir `CLAUDE.md` / l'historique de mise en place).
