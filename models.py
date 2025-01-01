# models.py
class PredictionModel:
    def __init__(self, team1_avg_stats, team2_avg_stats):
        self.team1_stats = team1_avg_stats
        self.team2_stats = team2_avg_stats
