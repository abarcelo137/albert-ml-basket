# 🏀 NBA Dream Team Predictor

---

## Introduction

**Y'a que la taille qui compte ?** *(Lataillequi)* est un projet réalisé en 2ème année du Bachelor Business & Data à **AlbertSchool**, dans le cadre du cours **Data: Deploying an ML Project**.

L'objectif principal est de prédire la meilleure équipe NBA de 5 joueurs (**Dream Team**) pour chaque saison grâce à des analyses statistiques avancées et à des modèles de Machine Learning. Une fonctionnalité additionnelle permet aussi de comparer deux lineups (aléatoires ou issues d'équipes réelles) pour déterminer objectivement laquelle serait la plus performante dans un match simulé.

---

## Objectif détaillé

Ce programme permet aux passionnés de basket, analystes sportifs et simples curieux de la NBA :

- **D’identifier** automatiquement la composition optimale de 5 joueurs NBA par saison.
- **De comparer** objectivement deux équipes et prévoir la gagnante selon des critères statistiques.
- **De valoriser** la complémentarité des joueurs selon leurs positions sur le terrain.

---

## Fonctionnalités principales

### 1. Prédiction de la Dream Team
- Sélection des meilleurs joueurs par poste (**Guard**, **Forward**, **Center**).
- Modèles utilisés : **Random Forest** et **Gradient Boosting**.
- Recherche exhaustive de la meilleure combinaison selon des métriques avancées.

### 2. Simulateur de Match
- Comparaison entre deux lineups :
  - **Équipes réelles** (5 meilleurs joueurs d’une équipe NBA sur une saison donnée).
  - **Aléatoires** (sélection individuelle de joueurs).
- Bonus de cohérence attribué selon la complémentarité des positions.

---

## Données utilisées

[Télécharger les datasets depuis Google Drive](https://drive.google.com/drive/folders/1K4sXEjIcb7b2yzsQfOt80cdB0G69IDzj?usp=sharing)

| Fichier                         | Description                                              |
|---------------------------------|----------------------------------------------------------|
| `all_seasons.csv`               | Statistiques individuelles des joueurs NBA               |
| `game.csv`, `line_score.csv`    | Résultats détaillés des matchs NBA                       |
| `player.csv`, `team.csv`        | Informations sur joueurs et équipes                      |
| `df_draft_combine_cleaned.csv`  | Mesures physiques des joueurs NBA                        |

Les données couvrent toutes les saisons NBA depuis l'an 2000.

---

## Structure du projet

```
.
├── data/                   # Datasets utilisés
├── notebooks/              # Notebooks d’analyse et modélisation
├── visualizations/         # Graphiques et visualisations
├── src/
│   └── lineup_predictor.py # Classe principale (LineupPredictor)
└── README.md               # Ce fichier
```

---

## Méthodologie

### Modélisation
- Modèles utilisés : **Random Forest** et **Gradient Boosting**.
- Optimisation des hyperparamètres via **GridSearchCV** (validation croisée).
- Métriques d'évaluation : **RMSE**, **R²**.

### Feature Engineering
- Statistiques normalisées par match (`pts_per_game`, `reb_per_game`, `ast_per_game`).
- Ratios avancés (`net_rating`, `ast_usg_ratio`, `reb_pct_sum`).
- Classification des postes en **Guard (G)**, **Forward (F)**, **Center (C)**.

### Bonus de Cohérence
- **+15 %** pour une répartition idéale (2G, 2F, 1C).
- **+10 %** pour présence des trois postes.
- **+5 %** pour seulement deux postes représentés.
- **−5 %** si un seul poste est représenté.

---

## Résultats & Visualisations
- 🥇 **Top Dream Teams** par saison.
- Graphiques comparatifs des performances (RMSE, R²).
- Analyse spécifique de la saison **2012** (lock-out NBA).

---

## Présentation du projet

➡️ [Présentation Canva du projet](https://www.canva.com/design/DAGnVLwCuhw/JlsmOdTvbZPZ0pkygkcseA/edit?utm_content=DAGnVLwCuhw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

---

## Contributeurs

- **Anna SPIRA**
- **Amandine BARCELO**
- **Keira CHANG**

---

*Projet réalisé dans le cadre du Bachelor Business & Data à AlbertSchool - Mai 2025*
