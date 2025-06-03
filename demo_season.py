#!/usr/bin/env python3
"""
Season simulation demo for the football simulation engine.

This script demonstrates how to simulate multiple games to create
season-like experiences with standings and statistics.
"""

import random
from collections import defaultdict
from data.team_loader import load_sample_teams
from simulation.game_engine import GameEngine


class SeasonSimulator:
    """Simple season simulator for demonstration purposes."""
    
    def __init__(self, teams):
        """Initialize the season simulator."""
        self.teams = teams
        self.standings = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0, 'points_for': 0, 'points_against': 0})
        self.games_played = []
    
    def simulate_divisional_games(self, num_games_per_team=4):
        """Simulate divisional games for all teams."""
        
        # Organize teams by division
        divisions = defaultdict(list)
        for team in self.teams:
            divisions[f"{team.conference} {team.division}"].append(team)
        
        print(f"Simulating {num_games_per_team} divisional games per team...")
        
        games_simulated = 0
        
        for division_name, div_teams in divisions.items():
            print(f"\n{division_name} Division Games:")
            
            # Each team plays every other team in division
            for i, home_team in enumerate(div_teams):
                for j, away_team in enumerate(div_teams):
                    if i != j and games_simulated < len(self.teams) * num_games_per_team // 2:
                        
                        # Create engine with random seed
                        engine = GameEngine(seed=random.randint(1, 100000))
                        result = engine.simulate_game(home_team, away_team)
                        
                        # Update standings
                        self._update_standings(result)
                        
                        # Track game
                        self.games_played.append(result)
                        games_simulated += 1
                        
                        # Display result
                        winner_text = result.winner.name if result.winner else "TIE"
                        print(f"  {away_team.name} @ {home_team.name}: {result.away_score}-{result.home_score} ({winner_text})")
        
        return games_simulated
    
    def simulate_random_games(self, num_games):
        """Simulate random matchups."""
        
        print(f"\nSimulating {num_games} additional cross-conference games...")
        
        for game_num in range(num_games):
            # Pick random teams from different conferences
            afc_teams = [t for t in self.teams if t.conference == "AFC"]
            nfc_teams = [t for t in self.teams if t.conference == "NFC"]
            
            home_team = random.choice(afc_teams + nfc_teams)
            # Pick opponent from different conference if possible
            if home_team.conference == "AFC":
                away_team = random.choice(nfc_teams)
            else:
                away_team = random.choice(afc_teams)
            
            engine = GameEngine(seed=random.randint(1, 100000))
            result = engine.simulate_game(home_team, away_team)
            
            self._update_standings(result)
            self.games_played.append(result)
            
            winner_text = result.winner.name if result.winner else "TIE"
            print(f"  Game {game_num + 1}: {away_team.name} @ {home_team.name}: {result.away_score}-{result.home_score} ({winner_text})")
    
    def _update_standings(self, result):
        """Update team standings based on game result."""
        home_key = f"{result.home_team.city} {result.home_team.name}"
        away_key = f"{result.away_team.city} {result.away_team.name}"
        
        # Update points
        self.standings[home_key]['points_for'] += result.home_score
        self.standings[home_key]['points_against'] += result.away_score
        self.standings[away_key]['points_for'] += result.away_score
        self.standings[away_key]['points_against'] += result.home_score
        
        # Update wins/losses/ties
        if result.home_score > result.away_score:
            self.standings[home_key]['wins'] += 1
            self.standings[away_key]['losses'] += 1
        elif result.away_score > result.home_score:
            self.standings[away_key]['wins'] += 1
            self.standings[home_key]['losses'] += 1
        else:
            self.standings[home_key]['ties'] += 1
            self.standings[away_key]['ties'] += 1
    
    def get_conference_standings(self, conference):
        """Get standings for a specific conference."""
        conf_teams = [t for t in self.teams if t.conference == conference]
        conf_standings = []
        
        for team in conf_teams:
            team_key = f"{team.city} {team.name}"
            record = self.standings[team_key]
            
            games_played = record['wins'] + record['losses'] + record['ties']
            win_pct = record['wins'] / games_played if games_played > 0 else 0
            
            conf_standings.append({
                'team': team_key,
                'wins': record['wins'],
                'losses': record['losses'],
                'ties': record['ties'],
                'win_pct': win_pct,
                'points_for': record['points_for'],
                'points_against': record['points_against'],
                'point_diff': record['points_for'] - record['points_against']
            })
        
        # Sort by win percentage, then by point differential
        conf_standings.sort(key=lambda x: (x['win_pct'], x['point_diff']), reverse=True)
        return conf_standings
    
    def print_standings(self):
        """Print current standings for both conferences."""
        
        print(f"\n{'='*80}")
        print("SEASON STANDINGS")
        print("=" * 80)
        
        for conference in ["AFC", "NFC"]:
            standings = self.get_conference_standings(conference)
            
            print(f"\n{conference} CONFERENCE")
            print("-" * 50)
            print(f"{'Rank':<4} {'Team':<25} {'W':<3} {'L':<3} {'T':<3} {'PCT':<6} {'PF':<4} {'PA':<4} {'DIFF':<5}")
            print("-" * 50)
            
            for i, team_record in enumerate(standings[:8]):  # Top 8 teams
                rank = i + 1
                print(f"{rank:<4} {team_record['team']:<25} "
                      f"{team_record['wins']:<3} {team_record['losses']:<3} {team_record['ties']:<3} "
                      f"{team_record['win_pct']:.3f:<6} "
                      f"{team_record['points_for']:<4} {team_record['points_against']:<4} "
                      f"{team_record['point_diff']:+d}")
    
    def get_season_stats(self):
        """Get overall season statistics."""
        total_games = len(self.games_played)
        total_points = sum(g.home_score + g.away_score for g in self.games_played)
        avg_points_per_game = total_points / total_games if total_games > 0 else 0
        
        home_wins = sum(1 for g in self.games_played if g.home_score > g.away_score)
        away_wins = sum(1 for g in self.games_played if g.away_score > g.home_score)
        ties = sum(1 for g in self.games_played if g.home_score == g.away_score)
        
        return {
            'total_games': total_games,
            'avg_points_per_game': avg_points_per_game,
            'home_wins': home_wins,
            'away_wins': away_wins,
            'ties': ties,
            'home_win_percentage': home_wins / total_games if total_games > 0 else 0
        }


def main():
    """Run a season simulation demo."""
    
    print("Football Simulation Engine - Season Demo")
    print("=" * 60)
    
    # Load teams
    teams = load_sample_teams()
    print(f"Loaded {len(teams)} NFL teams")
    
    # Create season simulator
    season = SeasonSimulator(teams)
    
    # Simulate divisional games
    divisional_games = season.simulate_divisional_games(2)  # 2 games per team in division
    
    # Simulate some cross-conference games
    season.simulate_random_games(16)
    
    # Show standings
    season.print_standings()
    
    # Show season statistics
    stats = season.get_season_stats()
    
    print(f"\n{'='*80}")
    print("SEASON STATISTICS")
    print("=" * 80)
    
    print(f"Total games simulated: {stats['total_games']}")
    print(f"Average points per game: {stats['avg_points_per_game']:.1f}")
    print(f"Home team wins: {stats['home_wins']} ({stats['home_win_percentage']*100:.1f}%)")
    print(f"Away team wins: {stats['away_wins']}")
    print(f"Ties: {stats['ties']}")
    
    # Find best and worst teams
    afc_standings = season.get_conference_standings("AFC")
    nfc_standings = season.get_conference_standings("NFC")
    
    if afc_standings and nfc_standings:
        best_afc = afc_standings[0]
        best_nfc = nfc_standings[0]
        worst_afc = afc_standings[-1]
        worst_nfc = nfc_standings[-1]
        
        print(f"\nPlayoff Picture:")
        print(f"AFC Leader: {best_afc['team']} ({best_afc['wins']}-{best_afc['losses']}-{best_afc['ties']})")
        print(f"NFC Leader: {best_nfc['team']} ({best_nfc['wins']}-{best_nfc['losses']}-{best_nfc['ties']})")
        
        print(f"\nNeed Improvement:")
        print(f"AFC: {worst_afc['team']} ({worst_afc['wins']}-{worst_afc['losses']}-{worst_afc['ties']})")
        print(f"NFC: {worst_nfc['team']} ({worst_nfc['wins']}-{worst_nfc['losses']}-{worst_nfc['ties']})")
    
    print(f"\n✅ Season simulation completed!")
    print("   This demonstrates the engine's capability for larger simulations.")


if __name__ == "__main__":
    main()
