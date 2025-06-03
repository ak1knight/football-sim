#!/usr/bin/env python3

# Debug script to test game_engine import
import sys
sys.path.append('.')

try:
    print("Trying to import game_engine module...")
    import simulation.game_engine as ge
    print(f"Module imported successfully: {ge}")
    print(f"Module attributes: {dir(ge)}")
    
    print("\nTrying to access GameEngine class...")
    if hasattr(ge, 'GameEngine'):
        print(f"GameEngine class found: {ge.GameEngine}")
    else:
        print("GameEngine class NOT found")
    
    print("\nTrying to access GameResult class...")
    if hasattr(ge, 'GameResult'):
        print(f"GameResult class found: {ge.GameResult}")
    else:
        print("GameResult class NOT found")
        
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()
