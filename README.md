# IDF Mobilité Assistant

<!-- HACS -->
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square&logo=HomeAssistantCommunityStore&logoColor=white)](https://github.com/hacs/integration)

<!-- Release -->
[![release](https://img.shields.io/github/v/release/yyrkoon94/idf-mobilite-assistant?style=flat-square)](https://github.com/yyrkoon94/idf-mobilite-assistant/releases)

<!-- Downloads -->
[![downloads](https://img.shields.io/github/downloads/yyrkoon94/idf-mobilite-assistant/total?style=flat-square)](https://github.com/yyrkoon94/idf-mobilite-assistant/releases)

<!-- Issues -->
[![issues](https://img.shields.io/github/issues/yyrkoon94/idf-mobilite-assistant?style=flat-square)](https://github.com/yyrkoon94/idf-mobilite-assistant/issues)

<!-- Companion Integration -->
[![companion_badge](https://img.shields.io/badge/Companion%20Integration-IDF%20Mobilité%20Card-5A4FCF?style=flat-square&logo=homeassistant&logoColor=white)](https://github.com/yyrkoon94/lovelace-idf-mobilite)

<!-- Home Assistant Integration -->
[![ha_integration](https://img.shields.io/badge/Home%20Assistant-Integration-03A9F4?style=flat-square&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)

<!-- Lovelace Ready -->
[![lovelace_ready](https://img.shields.io/badge/Lovelace-Ready-FFCA28?style=flat-square&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/lovelace)

<!-- Made for IDFM / PRIM API -->
[![prim_api](https://img.shields.io/badge/Made%20for-IDFM%20PRIM%20API-0078D4?style=flat-square)](https://prim.iledefrance-mobilites.fr/)

<!-- License -->
[![license](https://img.shields.io/github/license/yyrkoon94/idf-mobilite-assistant?style=flat-square)](https://github.com/yyrkoon94/idf-mobilite-assistant/blob/main/LICENSE)

[![made_in_idf](https://img.shields.io/badge/Made%20in-%C3%8Ele--de--France-E1000F?style=flat-square&logo=france&logoColor=white)](https://www.iledefrance.fr/)


---

## 🚇 Présentation

**IDF Mobilité Assistant** est une intégration Home Assistant permettant de créer automatiquement les capteurs nécessaires pour afficher les données temps réel d’Île‑de‑France Mobilités (IDFM) dans Home Assistant.

> 🧩 Cette intégration est le **compagnon officiel** de la Lovelace Card :
> **Ile de France Mobilité Card**
> 👉 https://github.com/yyrkoon94/lovelace-idf-mobilite
>
> Elle fournit *tous les sensors requis* pour alimenter la carte (horaires + perturbations).
>
> ⚠️ Les sensors seuls ne sont **pas destinés à être utilisés directement** dans Home Assistant.
> Ils sont optimisés pour être consommés par la carte Lovelace.

L’intégration utilise l’API **PRIM / Navitia v2** d’Île‑de‑France Mobilités pour fournir :

- les horaires en temps réel des arrêts (bus, métro, tram, RER, Transilien…)
- les messages de perturbation des lignes
- une configuration 100% UI, sans YAML
- une gestion propre des entités (création, suppression, regroupement)

---

## ✨ Fonctionnalités

### 🚌 Capteurs d’horaires (Lignes)
- Prochains passages en temps réel
- Direction
- Mode de transport (Bus, Métro, Tram, RER, Transilien…)
- Code ligne + couleur officielle IDFM
- Données Navitia complètes pour la Lovelace Card

### 📢 Capteurs de messages (Perturbations)
- Perturbations actives d’une ligne
- Détails des incidents (cause, impact, période, description)
- Données Navitia (`disruptions`, `line_reports`)
- Nom clair : *Message Bus 206*, *Message RER E*, etc.

### ⚙️ Configuration via UI
- Recherche d’arrêt par nom
- Recherche de ligne par code ou nom
- Ajout / suppression de capteurs
- Aucun YAML requis

### 🧹 Suppression propre des capteurs
- Suppression définitive dans l’Entity Registry
- Pas de capteurs “indisponibles”
- Regroupement automatique dans deux appareils :
  - **Lignes**
  - **Messages**

---

## 📦 Installation via HACS

### Méthode recommandée (Custom Repository)

1. Ouvrir **HACS → Intégrations**
2. Menu (⋮) → **Custom repositories**
3. Ajouter : https://github.com/yyrkoon94/idf-mobilite-assistant

4. Catégorie : **Integration**
5. Installer l’intégration
6. Redémarrer Home Assistant
7. Ajouter l’intégration via **Paramètres → Appareils & Services**

---

## 🔧 Configuration

### 1. Ajouter l’intégration
→ Home Assistant détecte automatiquement l’intégration après installation.

### 2. Ajouter un capteur d’horaires
- Rechercher un arrêt
- Sélectionner la ligne
- Le capteur apparaît dans le groupe **Lignes**

### 3. Ajouter un capteur de messages
- Rechercher une ligne
- Le capteur apparaît dans le groupe **Messages**

### 4. Supprimer un capteur
- Menu de l’intégration → **Supprimer un capteur**
- Suppression propre dans HA

---

## 🧩 Compatibilité Lovelace

Cette intégration est conçue **exclusivement** pour fonctionner avec :

👉 **Lovelace IDF Mobilité Card**
https://github.com/yyrkoon94/lovelace-idf-mobilite

Elle fournit :

- les sensors de passages
- les sensors de perturbations
- les métadonnées (couleurs, modes, codes…)
- les structures Navitia nécessaires à l’affichage

La carte Lovelace utilise ces sensors pour afficher :

- les prochains passages
- les perturbations
- les couleurs officielles IDFM
- les icônes de mode
- les correspondances multimodales

---

## 📝 Licence

Ce projet est distribué sous licence **MIT**.

