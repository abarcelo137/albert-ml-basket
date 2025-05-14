````markdown
# 🏀 NBA Dream Team Predictor

## Introduction

**Y'a que la taille qui compte?** (*Lataillequi*) est un projet réalisé dans le cadre du cours **Data: Deploying an ML Project** en deuxième année du Bachelor Business & Data à **AlbertSchool**.

L'objectif principal est de prédire la meilleure équipe NBA de 5 joueurs ("dream team") pour une saison donnée, en s’appuyant sur des analyses statistiques avancées et des modèles de Machine Learning. Ce projet propose également une fonctionnalité supplémentaire : comparer deux lineups de joueurs (aléatoires ou provenant d'équipes réelles NBA) pour prédire laquelle serait la plus performante lors d’un match simulé.

## Objectif détaillé

Ce programme aide les passionnés de basket, analystes sportifs ou simplement curieux de la NBA à :

- Identifier automatiquement la meilleure composition possible de 5 joueurs NBA pour chaque saison.
- Comparer objectivement deux équipes potentielles et prévoir la gagnante selon des critères statistiques précis.
- Valoriser la complémentarité des joueurs en fonction de leurs positions sur le terrain.

## Fonctionnalités

Le projet se divise en deux parties principales :

### 1. Prédiction de la Dream Team
- Sélection des meilleurs joueurs par poste (Guard, Forward, Center).
- Modèles utilisés : Random Forest et Gradient Boosting.
- Recherche exhaustive pour déterminer la meilleure combinaison selon des métriques avancées.

### 2. Simulateur de Match
- Comparaison de deux lineups :
  - Soit aléatoires (joueurs choisis individuellement).
  - Soit issues d'équipes réelles existantes pour une saison NBA donnée.
- Bonus de cohérence basé sur la complémentarité des postes.

## 📁 Données utilisées

Téléchargement des datasets : [Google Drive](https://drive.google.com/drive/folders/1K4sXEjIcb7b2yzsQfOt80cdB0G69IDzj?usp=sharing)

| Fichier                      | Description                                              |
|------------------------------|----------------------------------------------------------|
| `all_seasons.csv`            | Statistiques individuelles des joueurs                   |
| `game.csv`, `line_score.csv` | Résultats détaillés des matchs NBA                       |
| `player.csv`, `team.csv`     | Informations sur les joueurs et les équipes              |
| `df_draft_combine_cleaned.csv` | Mesures physiques des joueurs                          |

Les données couvrent toutes les saisons NBA depuis 2000.

## 🛠️ Structure du projet

```bash
.
├── data/                   # Datasets utilisés
├── notebooks/              # Notebooks d’analyse et modèles
├── visualizations/         # Graphiques générés
├── src/
│   └── lineup_predictor.py # Classe principale LineupPredictor
└── README.md               # Ce fichier
````

## Méthodologie

### Modélisation

* Entraînement des modèles Random Forest et Gradient Boosting.
* Hyperparamètres optimisés par validation croisée (GridSearchCV).
* Métriques d'évaluation : RMSE et R².

### Feature Engineering

* Statistiques par match (`pts_per_game`, `reb_per_game`, `ast_per_game`).
* Ratios avancés (`net_rating`, `ast_usg_ratio`, `reb_pct_sum`).
* Classification simplifiée des postes en Guard (G), Forward (F), Center (C).

### Bonus de Cohérence

* +15% pour une répartition idéale (2 Guards, 2 Forwards, 1 Center).
* +10% pour présence des trois postes.
* +5% pour deux postes seulement.
* −5% si un seul poste représenté.

## Résultats & Visualisations

* Top Dream Teams par saison.
* Graphiques comparatifs des performances modèles (RMSE, R²).
* Analyse de l’anomalie de la saison 2012 (lock-out).

## Présentation du projet

[Lien vers la présentation Canva](https://www.canva.com/design/DAGnVLwCuhw/JlsmOdTvbZPZ0pkygkcseA/edit?utm_content=DAGnVLwCuhw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

## Contributeurs

* **\[Anna SPIRA]**
* **\[Amandine BARCELO]**
* **\[Keira CHANG]**

---

*Projet réalisé dans le cadre d'AlbertSchool - Mai 2025*
