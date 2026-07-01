#!/usr/bin/env python3
"""
rebuild_manifest.py — régénère 02_Asset/runtime/manifest.json à partir des PNG
présents, puis affiche l'audit de cohérence PACK(HTML) ⇄ manifest ⇄ fichiers.

À lancer après tout ajout/suppression manuel d'un PNG dans runtime/.

Usage : python3 tools/rebuild_manifest.py
"""
import asset_lib as A

if __name__ == "__main__":
    keys = A.rebuild_manifest()
    print("manifest.json régénéré :", len(keys), "clés")
    rep = A.audit()
    print("Audit cohérence :")
    for k, v in rep.items():
        print("  %-16s %s" % (k, v))
    if rep["png_sans_pack"]:
        print("\n⚠️ PNG présents mais absents du tableau PACK (jamais chargés par le jeu) :")
        print("  ", rep["png_sans_pack"])
        print("  → ajoute-les au `const PACK=[...]` du HTML si tu veux qu'ils s'affichent.")
    print("\nOK.")
