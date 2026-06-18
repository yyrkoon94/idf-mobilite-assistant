# Changelog
Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au principe de versionnage sémantique (SemVer).

---

## [0.1.0] - 2026-06-18
### Ajouté
- Première version publique de l’intégration **IDF Mobilité Assistant**.
- Support complet des capteurs d’horaires (lignes) basés sur l’API PRIM / Navitia.
- Support complet des capteurs de messages (perturbations) par ligne.
- Interface de configuration 100% UI (aucun YAML requis).
- Recherche d’arrêt et de ligne directement dans le flux de configuration.
- Gestion propre des entités : création, suppression définitive, regroupement par type.
- Icônes dynamiques selon le mode de transport (Bus, Métro, Tram, RER, Transilien…).
- Icône dédiée pour les capteurs de messages.
- Compatibilité totale avec la Lovelace Card :
  **Ile de France Mobilité Card** (https://github.com/yyrkoon94/lovelace-idf-mobilite)
- Ajout du fichier `hacs.json` pour compatibilité HACS.
- Ajout des métadonnées nécessaires dans `manifest.json` (version, documentation, issue tracker).
- Première release GitHub.

---

## [Unreleased]
### Prévu
- Améliorations mineures et correctifs selon retours utilisateurs.
