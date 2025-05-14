import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import random
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class LineupPredictor:
    def __init__(self):
        self.players_data = None
        self.draft_combine_data = None
        self.game_data = None
        self.team_stats = None
        self.model = None
        self.features = None
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Charge et prépare les données nécessaires"""
        # Charger les données des joueurs
        self.players_data = pd.read_csv('/Users/spira/Desktop/Cours Albert B2/Data/NBA/Data final/df_v1.csv',sep=';')
        
        # Charger les données du draft combine (uniquement pour l'affichage)
        self.draft_combine_data = pd.read_csv('/Users/spira/Desktop/Cours Albert B2/Data/NBA/Data final/df_draft_combine_cleaned.csv')
        
        # Charger les données des matchs
        self.game_data = pd.read_csv('/Users/spira/Desktop/Cours Albert B2/Data/NBA/Data final/df_game_summary_cleaned.csv')
        
        # Convertir les saisons au même format et filtrer après 2000
        self.players_data['season_year'] = self.players_data['season'].str[:4].astype(int)
        self.players_data = self.players_data[self.players_data['season_year'] >= 2000]
        
        # Nettoyer et préparer les données
        self._clean_and_prepare_data()
        
        # Calculer les statistiques d'équipe
        self._calculate_team_stats()
        
        # Entraîner le modèle
        self._train_model()
        
    def _clean_and_prepare_data(self):
        """Nettoie et prépare les données des joueurs"""
        # Feature engineering pour les joueurs
        self.players_data['pts_per_game'] = self.players_data['pts'] / self.players_data['gp']
        self.players_data['reb_per_game'] = self.players_data['reb'] / self.players_data['gp']
        self.players_data['ast_per_game'] = self.players_data['ast'] / self.players_data['gp']
        self.players_data['ast_usg_ratio'] = self.players_data['ast_pct'] / (self.players_data['usg_pct'] + 1e-6)
        self.players_data['reb_pct_sum'] = self.players_data['oreb_pct'] + self.players_data['dreb_pct']
        
        # Ajouter des statistiques avancées
        self.players_data['efficiency'] = (self.players_data['pts'] + self.players_data['reb'] + self.players_data['ast']) / self.players_data['gp']
        self.players_data['scoring_efficiency'] = self.players_data['pts_per_game'] / (self.players_data['usg_pct'] + 1e-6)
        self.players_data['playmaking'] = self.players_data['ast_per_game'] * self.players_data['ast_pct']
        
        # Gestion des positions
        def get_primary_pos(pos):
            if pd.isna(pos):
                return np.nan
            pos = str(pos).upper()
            if "GUARD" in pos and "CENTER" not in pos:
                return "G"
            if "CENTER" in pos:
                return "C"
            if "FORWARD" in pos:
                return "F"
            return np.nan
        
        self.players_data['primary_pos'] = self.players_data['position'].apply(get_primary_pos)
        
        # Préparer les données des matchs
        if self.game_data is not None:
            # Créer deux dataframes séparés pour les équipes à domicile et à l'extérieur
            home_games = self.game_data.copy()
            visitor_games = self.game_data.copy()
            
            # Renommer les colonnes pour la fusion
            home_games = home_games.rename(columns={'home_team_id': 'team_id'})
            visitor_games = visitor_games.rename(columns={'visitor_team_id': 'team_id'})
            
            # Combiner les deux dataframes
            all_games = pd.concat([home_games, visitor_games], ignore_index=True)
            
            # Calculer les statistiques moyennes par équipe et par saison
            game_stats = all_games.groupby(['season', 'team_id']).agg({
                'game_id': 'count'  # Nombre de matchs joués
            }).reset_index()
            
            # Renommer la colonne de compte
            game_stats = game_stats.rename(columns={'game_id': 'games_played'})
            
            # Fusionner avec les données des joueurs
            # Note: Nous devons d'abord nous assurer que team_id correspond à team_abbreviation
            # Pour l'instant, nous allons simplement ajouter les statistiques de base
            self.players_data['games_played'] = self.players_data['gp']
        
        # Remplacer les valeurs manquantes
        numeric_columns = [
            'pts_per_game', 'reb_per_game', 'ast_per_game',
            'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct',
            'net_rating', 'ast_usg_ratio', 'reb_pct_sum', 'win_rate',
            'efficiency', 'scoring_efficiency', 'playmaking'
        ]
        
        for col in numeric_columns:
            if col in self.players_data.columns:
                self.players_data[col] = self.players_data[col].fillna(self.players_data[col].mean())
        
    def _calculate_team_stats(self):
        """Calcule les statistiques d'équipe"""
        # Statistiques de base
        self.team_stats = self.players_data.groupby('team_abbreviation').agg({
            'win_rate': 'mean',
            'pts_per_game': 'mean',
            'reb_per_game': 'mean',
            'ast_per_game': 'mean',
            'net_rating': 'mean',
            'ts_pct': 'mean',
            'ast_usg_ratio': 'mean',
            'reb_pct_sum': 'mean',
            'efficiency': 'mean',
            'scoring_efficiency': 'mean',
            'playmaking': 'mean'
        }).reset_index()
        
    def _train_model(self):
        """Entraîne le modèle de prédiction"""
        # Définir les features pour le modèle
        features_all = [
            'pts_per_game', 'reb_per_game', 'ast_per_game',
            'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct',
            'net_rating', 'ast_usg_ratio', 'reb_pct_sum',
            'efficiency', 'scoring_efficiency', 'playmaking'
        ]
        
        # Calculer les corrélations avec win_rate
        corr = self.players_data[features_all + ['win_rate']].corr()
        corr_win = corr['win_rate'].abs().drop('win_rate').sort_values(ascending=False)
        
        # Sélectionner les 8 meilleures features
        self.features = corr_win.index.tolist()[:8]
        
        # Préparer les données d'entraînement
        train_data = self.players_data.groupby(['season_year', 'team_abbreviation']).apply(
            lambda x: x.nlargest(5, 'pts')
        ).reset_index(drop=True)
        
        # Agréger les statistiques par équipe
        team_stats = train_data.groupby(['season_year', 'team_abbreviation'])[self.features].mean().reset_index()
        
        # Fusionner avec le winrate
        team_stats = pd.merge(
            team_stats,
            self.players_data[['season_year', 'team_abbreviation', 'win_rate']].drop_duplicates(),
            on=['season_year', 'team_abbreviation']
        )
        
        # Entraîner le modèle
        X = team_stats[self.features]
        y = team_stats['win_rate']
        
        self.model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
        self.model.fit(X, y)
        
    def get_lineup_coherence(self, lineup: List[Dict]) -> Tuple[float, str]:
        """Calcule la cohérence d'un lineup et retourne le bonus et la description"""
        # Ne considérer que les positions connues (non-NaN)
        positions = [player['position'] for player in lineup if pd.notna(player['position'])]
        if not positions:  # Si aucune position n'est connue
            return 1.0, "Positions inconnues"
            
        unique_positions = set(positions)
        
        # Vérifier la présence de chaque position
        has_guard = 'G' in unique_positions
        has_forward = 'F' in unique_positions
        has_center = 'C' in unique_positions
        
        # Compter le nombre de positions uniques
        num_unique_positions = len(unique_positions)
        
        # Définir les bonus selon la cohérence
        if num_unique_positions == 3 and positions.count('G') == 2 and positions.count('F') == 2 and positions.count('C') == 1:
            return 1.15, "Lineup parfaite (2G, 2F, 1C)"
        elif num_unique_positions == 3:
            return 1.10, "Lineup avec les 3 positions (G, F, C)"
        elif num_unique_positions == 2:
            if has_guard and has_forward:
                return 1.05, "Lineup avec Guards et Forwards"
            elif has_guard and has_center:
                return 1.05, "Lineup avec Guards et Center"
            elif has_forward and has_center:
                return 1.05, "Lineup avec Forwards et Center"
        elif num_unique_positions == 1:
            return 0.95, "Lineup avec une seule position"
        
        return 1.0, "Lineup standard"
        
    def select_random_lineup(self) -> List[Dict]:
        """Sélectionne aléatoirement une lineup de 5 joueurs"""
        # Sélectionner 5 joueurs au hasard parmi les meilleurs
        top_players = self.players_data.nlargest(100, 'efficiency')
        selected_players = top_players.sample(n=5)
        
        lineup = []
        for _, player in selected_players.iterrows():
            stats = {
                'pts_per_game': player['pts_per_game'],
                'reb_per_game': player['reb_per_game'],
                'ast_per_game': player['ast_per_game'],
                'net_rating': player['net_rating'],
                'oreb_pct': player['oreb_pct'],
                'dreb_pct': player['dreb_pct'],
                'usg_pct': player['usg_pct'],
                'ts_pct': player['ts_pct'],
                'ast_pct': player['ast_pct'],
                'ast_usg_ratio': player['ast_usg_ratio'],
                'reb_pct_sum': player['reb_pct_sum'],
                'efficiency': player['efficiency'],
                'scoring_efficiency': player['scoring_efficiency'],
                'playmaking': player['playmaking']
            }
            
            # Ajouter les données du draft combine si disponibles
            combine_data = {}
            if 'player_name' in self.draft_combine_data.columns:
                player_combine = self.draft_combine_data[self.draft_combine_data['player_name'] == player['player_name']]
                if not player_combine.empty:
                    combine_data = {
                        'height': player_combine['height_wo_shoes_cm'].iloc[0],
                        'wingspan': player_combine['wingspan_cm'].iloc[0],
                        'standing_reach': player_combine['standing_reach_cm'].iloc[0],
                        'body_fat': player_combine['body_fat_pct'].iloc[0],
                        'vertical_leap': player_combine['standing_vertical_leap'].iloc[0],
                        'max_vertical': player_combine['max_vertical_leap'].iloc[0],
                        'agility': player_combine['lane_agility_time'].iloc[0],
                        'sprint': player_combine['three_quarter_sprint'].iloc[0]
                    }
            
            lineup.append({
                'player_id': player.get('person_id'),
                'name': player['player_name'],
                'position': player['primary_pos'],
                'team': player['team_abbreviation'],
                'stats': stats,
                'combine_data': combine_data
            })
        
        return lineup
    
    def calculate_lineup_score(self, lineup: List[Dict]) -> Tuple[float, str]:
        """Calcule le score d'une lineup basé sur les statistiques des joueurs et de l'équipe"""
        # Calculer les statistiques moyennes de la lineup
        lineup_stats = pd.DataFrame([player['stats'] for player in lineup])
        avg_stats = lineup_stats[self.features].mean()
        
        # Prédire le winrate avec le modèle
        predicted_winrate = self.model.predict(avg_stats.values.reshape(1, -1))[0]
        
        # Calculer le bonus de cohérence
        coherence_bonus, coherence_desc = self.get_lineup_coherence(lineup)
        
        # Appliquer le bonus de cohérence
        predicted_winrate *= coherence_bonus
        
        # S'assurer que le winrate reste dans des limites raisonnables
        predicted_winrate = max(0.0, min(predicted_winrate, 1.0))
        
        return predicted_winrate, coherence_desc
    
    def predict_winner(self, lineup1: List[Dict], lineup2: List[Dict]) -> Tuple[List[Dict], float, float, str, str]:
        """Prédit le gagnant entre deux lineups"""
        score1, desc1 = self.calculate_lineup_score(lineup1)
        score2, desc2 = self.calculate_lineup_score(lineup2)
        
        if score1 > score2:
            return lineup1, score1, score2, desc1, desc2
        else:
            return lineup2, score2, score1, desc2, desc1

# Exemple d'utilisation
if __name__ == "__main__":
    predictor = LineupPredictor()
    predictor.load_data()
    
    # Sélectionner deux lineups aléatoires
    lineup1 = predictor.select_random_lineup()
    lineup2 = predictor.select_random_lineup()
    
    # Prédire le gagnant
    winner, winner_score, loser_score, winner_desc, loser_desc = predictor.predict_winner(lineup1, lineup2)
    
    print("Lineup 1:")
    for player in lineup1:
        print(f"{player['position']}: {player['name']} ({player['team']})")
        if player['combine_data']:
            print(f"  Combine: {player['combine_data']}")
    print(f"Winrate prédit: {winner_score if winner == lineup1 else loser_score:.3f}")
    print(f"Description: {winner_desc if winner == lineup1 else loser_desc}")
    
    print("\nLineup 2:")
    for player in lineup2:
        print(f"{player['position']}: {player['name']} ({player['team']})")
        if player['combine_data']:
            print(f"  Combine: {player['combine_data']}")
    print(f"Winrate prédit: {winner_score if winner == lineup2 else loser_score:.3f}")
    print(f"Description: {winner_desc if winner == lineup2 else loser_desc}")
    
    print("\nGagnant prédit:")
    for player in winner:
        print(f"{player['position']}: {player['name']} ({player['team']})")
        if player['combine_data']:
            print(f"  Combine: {player['combine_data']}")
    print(f"Winrate prédit: {winner_score:.3f}")
    print(f"Description: {winner_desc}") 