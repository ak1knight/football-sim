#!/usr/bin/env python3
"""
Season simulation demonstration for the football simulation engine.

This script demonstrates the full season management workflow:
1. Create a season with schedule generation
2. Get next games to simulate
3. Simulate games using the game engine
4. Submit results back to season engine
5. Track standings and playoff picture
"""

import random
from api.season_api import SeasonAPI
from simulation.game_engine import GameEngine


def demonstrate_season_workflow():
    """Demonstrate the complete season management workflow."""
    
    print("🏈 NFL Season Management Demo")
    print("="*60)
    
    # Initialize the season API
    season_api = SeasonAPI()
    
    # Step 1: Create a new season
    print("\n📅 Step 1: Creating New Season")
    print("-" * 30)
    
    season_result = season_api.create_season(season_year=2024, seed=42)
    if not season_result['success']:
        print(f"❌ Failed to create season: {season_result['error']}")
        return
    
    print(f"✅ {season_result['message']}")
    print(f"   Teams: {season_result['total_teams']}")
    print(f"   Total Games: {season_result['total_games']}")
    print(f"   Current Week: {season_result['season_status']['current_week']}")
    
    # Step 2: Show initial standings
    print("\n📊 Step 2: Initial Standings (AFC East)")
    print("-" * 30)
    
    standings_result = season_api.get_standings(by_division=True)
    if standings_result['success']:
        afc_east = standings_result['standings'].get('AFC East', [])
        for i, team in enumerate(afc_east, 1):
            record = f"{team['wins']}-{team['losses']}"
            if team['ties'] > 0:
                record += f"-{team['ties']}"
            print(f"   {i}. {team['team']['city']} {team['team']['name']} ({record})")
    
    # Step 3: Simulate first few weeks
    print("\n🎮 Step 3: Simulating First 3 Weeks")
    print("-" * 30)
    
    game_engine = GameEngine(enable_reporting=False)
    
    for week in range(1, 4):  # Simulate weeks 1-3
        print(f"\n   Week {week} Games:")
        
        # Get games for this week
        week_games_result = season_api.get_week_games(week)
        if not week_games_result['success']:
            print(f"   ❌ Failed to get week {week} games")
            continue
        
        week_games = week_games_result['games']
        print(f"   Found {len(week_games)} games to simulate")
        
        # Simulate each game
        for game_data in week_games:
            if game_data['status'] == 'scheduled':
                # Find the actual team objects
                home_team = None
                away_team = None
                
                for team in season_api.teams:
                    if team.abbreviation == game_data['home_team']['abbreviation']:
                        home_team = team
                    if team.abbreviation == game_data['away_team']['abbreviation']:
                        away_team = team
                
                if home_team and away_team:
                    # Simulate the game
                    result = game_engine.simulate_game(home_team, away_team)
                    
                    # Submit result to season engine
                    submit_result = season_api.submit_game_result(
                        game_id=game_data['game_id'],
                        home_score=result.home_score,
                        away_score=result.away_score,
                        overtime=(result.duration > 60),
                        game_duration=result.duration
                    )
                    
                    if submit_result['success']:
                        winner = "TIE" if result.home_score == result.away_score else (
                            home_team.abbreviation if result.home_score > result.away_score 
                            else away_team.abbreviation
                        )
                        print(f"      {away_team.abbreviation} @ {home_team.abbreviation}: "
                              f"{result.away_score}-{result.home_score} ({winner})")
                    else:
                        print(f"      ❌ Failed to submit result: {submit_result['error']}")
    
    # Step 4: Show updated standings
    print("\n📊 Step 4: Standings After 3 Weeks")
    print("-" * 30)
    
    standings_result = season_api.get_standings(by_division=True)
    if standings_result['success']:
        print("\n   AFC East:")
        afc_east = standings_result['standings'].get('AFC East', [])
        for i, team in enumerate(afc_east, 1):
            record = f"{team['wins']}-{team['losses']}"
            if team['ties'] > 0:
                record += f"-{team['ties']}"
            pct = team['win_percentage']
            pf = team['points_for']
            pa = team['points_against']
            print(f"      {i}. {team['team']['city']} {team['team']['name']} "
                  f"({record}, {pct:.3f}, PF:{pf}, PA:{pa})")
        
        print("\n   NFC East:")
        nfc_east = standings_result['standings'].get('NFC East', [])
        for i, team in enumerate(nfc_east, 1):
            record = f"{team['wins']}-{team['losses']}"
            if team['ties'] > 0:
                record += f"-{team['ties']}"
            pct = team['win_percentage']
            pf = team['points_for']
            pa = team['points_against']
            print(f"      {i}. {team['team']['city']} {team['team']['name']} "
                  f"({record}, {pct:.3f}, PF:{pf}, PA:{pa})")
    
    # Step 5: Show team schedule
    print("\n📅 Step 5: Sample Team Schedule (Buffalo Bills)")
    print("-" * 30)
    
    schedule_result = season_api.get_team_schedule('BUF')
    if schedule_result['success']:
        print(f"   Team Record: {schedule_result['record']['wins']}-{schedule_result['record']['losses']}")
        print(f"   Games Played: {schedule_result['record']['games_played']}/17")
        
        print(f"\n   Next 5 Games:")
        upcoming_games = [g for g in schedule_result['schedule'] if g['status'] == 'scheduled'][:5]
        for game in upcoming_games:
            home_away = "vs" if game['is_home'] else "@"
            opponent = game['opponent']['abbreviation']
            print(f"      Week {game['week']}: {home_away} {opponent}")
    
    # Step 6: Show season status
    print("\n📈 Step 6: Season Status")
    print("-" * 30)
    
    status_result = season_api.get_season_status()
    if status_result['success']:
        status = status_result['season_status']
        print(f"   Current Week: {status['current_week']}")
        print(f"   Phase: {status['current_phase'].replace('_', ' ').title()}")
        print(f"   Games Completed: {status['completed_games']}/{status['total_games']} "
              f"({status['completion_percentage']}%)")
        print(f"   Weeks Remaining: {status['weeks_remaining']}")
    
    # Step 7: Show next games to simulate
    print("\n🎯 Step 7: Next Games Ready for Simulation")
    print("-" * 30)
    
    next_games_result = season_api.get_next_games(limit=8)
    if next_games_result['success']:
        print(f"   Found {next_games_result['count']} games ready for simulation:")
        for game in next_games_result['games'][:8]:
            home_team = game['home_team']['abbreviation']
            away_team = game['away_team']['abbreviation']
            week = game['week']
            print(f"      Week {week}: {away_team} @ {home_team} (ID: {game['game_id']})")
    
    print("\n✅ Season Management Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("- ✅ Season creation with automatic scheduling")
    print("- ✅ Game simulation integration")
    print("- ✅ Automatic standings updates")
    print("- ✅ Team schedule tracking")
    print("- ✅ Season progress monitoring")
    print("- ✅ Next games queue management")


def demonstrate_api_integration():
    """Demonstrate how a frontend would integrate with the season API."""
    
    print("\n🌐 Frontend Integration Example")
    print("="*60)
    
    season_api = SeasonAPI()
    
    # Frontend would call these endpoints:
    print("\n1. Initialize Season:")
    print("   POST /api/season/create")
    result = season_api.create_season(2024, seed=12345)
    print(f"   Response: {result['success']} - {result.get('message', result.get('error'))}")
    
    print("\n2. Get Teams:")
    print("   GET /api/teams")
    teams_result = season_api.get_all_teams()
    print(f"   Response: {teams_result['total_teams']} teams loaded")
    
    print("\n3. Get Next Games to Simulate:")
    print("   GET /api/season/next-games?limit=4")
    next_games = season_api.get_next_games(4)
    print(f"   Response: {next_games['count']} games ready")
    
    if next_games['success'] and next_games['games']:
        sample_game = next_games['games'][0]
        print(f"\n4. Simulate Game (Frontend calls game engine):")
        print(f"   Game: {sample_game['away_team']['abbreviation']} @ {sample_game['home_team']['abbreviation']}")
        
        # Simulate a sample result
        print(f"   POST /api/game/simulate")
        print(f"   Body: {{'home_team': '{sample_game['home_team']['abbreviation']}', 'away_team': '{sample_game['away_team']['abbreviation']}'}}")
        
        # Fake a game result
        home_score = random.randint(14, 35)
        away_score = random.randint(10, 31)
        
        print(f"\n5. Submit Game Result:")
        print(f"   POST /api/season/game-result")
        result = season_api.submit_game_result(
            sample_game['game_id'], 
            home_score, 
            away_score
        )
        print(f"   Response: {result['success']} - {result.get('message', result.get('error'))}")
        
        print(f"\n6. Get Updated Standings:")
        print(f"   GET /api/season/standings")
        standings = season_api.get_standings()
        print(f"   Response: Standings updated for week {standings.get('last_updated', 'N/A')}")
    
    print("\n✅ API Integration Demo Complete!")


if __name__ == "__main__":
    # Run the main demonstration
    demonstrate_season_workflow()
    
    # Show API integration patterns
    demonstrate_api_integration()
