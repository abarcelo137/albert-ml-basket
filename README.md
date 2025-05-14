# Y'a que la taille qui compte?

Lataillequi est un projet réalisé en 2e année de Bachelor Business & Data à AlbertSchool dans le cadre du cours de _Data: Deploying an ML project_ afin de prédire l'équipe de basketteurs idéale pour gagner un match.

### Présentation

```bash
https://www.canva.com/design/DAGnVLwCuhw/JlsmOdTvbZPZ0pkygkcseA/edit?utm_content=DAGnVLwCuhw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
```

### Datasets

Téléchargement des données: 
```bash
https://drive.google.com/drive/folders/1K4sXEjIcb7b2yzsQfOt80cdB0G69IDzj?usp=sharing
```
Le projet repose sur un ensemble de fichiers issus de l’API de la NBA, de Kaggle ou de sources publiques NBA, portant sur plusieurs saisons. Les données sont structurées autour de trois axes :

- *Statistiques individuelles des joueurs* (all_seasons.csv) : points, passes, rebonds, efficacité au tir, rating d’impact, etc.
- *Résultats de match* (game.csv, line_score.csv) : scores finaux, identifiants d’équipes, issue du match.
- *Référentiels d'identité* (player.csv) : identifiants et noms complets des joueurs.

Ces données couvrent plusieurs saisons NBA, permettent de relier les performances individuelles à des résultats collectifs, et sont utilisées pour analyser l’impact de compositions d’équipes. Ces fichiers contiennent des **statistiques individuelles et collectives**, des **résultats de match**s, des **informations d’identité des joueurs et des équipes**, ainsi que des détails sur les compositions match par match.

# NBA Dream Team Predictor

## 🏀 Objectif
Prédire automatiquement la meilleure composition de 5 joueurs NBA ("dream team") par saison - la combinaison qui maximise les chances de victoire de l'équipe.

## 📊 Datasets
- **all_seasons.csv**: Statistiques par joueur et par saison (points, rebonds, passes, usage, efficacité, etc.)
- **game.csv**: Résultats des matchs avec équipes et scores
- **player.csv**: Identifiants et noms des joueurs
- **common_player.csv**: Liens entre joueurs et équipes
- **line_score.csv**: Scores par équipe pour chaque match
- **team.csv**: Informations sur les équipes

## 🔍 Feature Engineering
Le modèle utilise plusieurs métriques calculées pour évaluer l'impact des joueurs:

1. **Stats normalisées par match**
   - `pts_per_game` = `pts` / `gp` (points par match)
   - `reb_per_game` = `reb` / `gp` (rebonds par match)
   - `ast_per_game` = `ast` / `gp` (passes par match)

2. **Ratios avancés**
   - `ast_usg_ratio` = `ast_pct` / `usg_pct` (efficacité de création)
   - `reb_pct_sum` = `oreb_pct` + `dreb_pct` (impact global au rebond)
   - `net_rating` (différentiel offensif/défensif par 100 possessions)

3. **Postes de jeu**
   - Extraction du poste primaire: **G** (Guard), **F** (Forward), **C** (Center)

## 🤖 Modélisation
Pour chaque saison, nous suivons un processus rigoureux:

1. **Entraînement**
   - Données: toutes les saisons sauf celle évaluée
   - Features: moyennes des statistiques des 5 meilleurs scoreurs par équipe
   - Target: `win_rate` de l'équipe

2. **Comparaison de modèles**
   - **Random Forest Regressor**: modèle ensemble robuste aux outliers
   - **Gradient Boosting Regressor**: modèle séquentiel généralement plus précis

3. **Métriques d'évaluation**
   - **RMSE** (Root Mean Square Error): mesure la précision des prédictions
   - **R²**: pourcentage de variance expliquée par le modèle
   
4. **Fine-tuning des hyperparamètres** (tous les 5 ans)
   - Optimisation par GridSearchCV avec validation croisée
   - Paramètres optimisés: nombre d'arbres, profondeur, critères de division, etc.

5. **Recherche de la Dream Team**
   - Définition d'un pool de candidats: Top joueurs par position selon `net_rating`
   - Évaluation de toutes les combinaisons valides (2G-2F-1C)
   - Sélection de la composition avec le meilleur taux de victoire prédit

## 📈 Résultats et Visualisations
Le script génère plusieurs outputs:

- **Fichiers CSV**:
  - Métriques de performance par saison
  - Dream Teams calculées par Random Forest
  - Dream Teams calculées par Gradient Boosting

- **Visualisations**:
  - Comparaison des RMSE par saison
  - Comparaison des scores R² par saison
  - Analyse de l'anomalie observée pour 2012 (saison réduite par lock-out)

Voici une version consolidée et prête à être collée dans ton `README.md`, intégrant proprement la partie avec les lineups d'équipes réelles :

---

## PARTIE 2 — Comparaison de deux lineups

Le projet permet de **comparer deux lineups NBA** et de **prédire laquelle est la plus performante dans un match simulé**. Deux approches sont proposées :

* **Lineups aléatoires** composés de 5 joueurs sélectionnés individuellement
* **Lineups réels** issus d’équipes NBA existantes sur une saison donnée

Ces deux variantes utilisent le même modèle de prédiction et les mêmes métriques, permettant de comparer à la fois la qualité intrinsèque des joueurs et la cohérence collective d'une équipe.

### Structure du code

Le cœur du système repose sur la classe `LineupPredictor`, qui permet de comparer deux lineups (aléatoires ou réels) et de prédire un vainqueur :

```python
class LineupPredictor:
    def __init__(self)
    def load_data()
    def _clean_and_prepare_data()
    def _calculate_team_stats()
    def _train_model()
    def get_lineup_coherence(lineup)
    def select_random_lineup()
    def select_team_lineup(team_name, season)
    def calculate_lineup_score(lineup)
    def predict_winner(lineup1, lineup2)
```

### Datasets utilisés

* `df_v1.csv` : Statistiques individuelles des joueurs par saison (issu de la Partie 1)
* `df_draft_combine_cleaned.csv` : Données physiques des joueurs
* `df_game_summary_cleaned.csv` : Résultats de matchs NBA

Les données sont filtrées pour ne conserver que les saisons après 2000.

### Feature Engineering

Le système calcule plusieurs métriques avancées pour chaque joueur :

#### 1. Statistiques par match :

* `pts_per_game`, `reb_per_game`, `ast_per_game`

#### 2. Métriques d'efficacité :

* `efficiency` = `(pts + reb + ast) / gp`
* `scoring_efficiency` = `pts_per_game / usg_pct`
* `playmaking` = `ast_per_game * ast_pct`
* `ast_usg_ratio` = `ast_pct / usg_pct`
* `reb_pct_sum` = `oreb_pct + dreb_pct`

#### 3. Classification des positions :

* `G` : Guard
* `F` : Forward
* `C` : Center

### Modèle de prédiction

Un modèle `RandomForestRegressor` est entraîné pour prédire le **taux de victoire (`win_rate`)** d’un lineup à partir des statistiques agrégées de ses joueurs.

* Sélection des 8 features les plus corrélées avec `win_rate`
* Agrégation des statistiques des 5 meilleurs scoreurs de chaque équipe
* Entraînement du modèle : 200 arbres, profondeur maximale de 10

### Systèmes de sélection de lineup

Deux méthodes sont disponibles :

1. `select_random_lineup()` : sélectionne aléatoirement 5 joueurs parmi tout l'historique NBA
2. `select_team_lineup(team_name, season)` : sélectionne les 5 meilleurs joueurs (au scoring) d’une **équipe réelle** pour une saison donnée

Dans les deux cas, les statistiques individuelles sont récupérées et les positions des joueurs sont utilisées pour évaluer la cohérence de la lineup.

### Système de bonus de cohérence

Un bonus est appliqué au taux de victoire prédit en fonction de la distribution des postes :

* **+15%** pour une lineup idéale (2 Guards, 2 Forwards, 1 Center)
* **+10%** pour une lineup avec les 3 positions représentées
* **+5%** pour une lineup avec 2 types de positions
* **−5%** pour une lineup composée d’un seul type de poste

### Procédure de prédiction

1. Sélection de deux lineups (aléatoires ou réelles)
2. Calcul des statistiques agrégées
3. Prédiction du `win_rate` via le modèle RandomForest
4. Application du bonus de cohérence
5. Comparaison des scores finaux
6. Affichage détaillé des joueurs et du score du lineup gagnant

---

Cette architecture permet de comparer objectivement la performance de deux lineups selon les statistiques avancées, tout en valorisant la **complémentarité des postes** et la **logique collective d’une équipe réelle**.
