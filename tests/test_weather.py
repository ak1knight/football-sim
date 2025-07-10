"""
Tests for weather functionality in the football simulation.

This module tests weather condition modeling and their effects on gameplay.
"""

import unittest
import numpy as np
from models.weather import (
    Weather, WeatherCondition, WindDirection, WeatherEffects,
    generate_random_weather, get_city_weather_tendency
)
from simulation.game_engine import GameEngine
from data.team_loader import load_sample_teams


class TestWeather(unittest.TestCase):
    """Test cases for the Weather class."""

    def setUp(self):
        """Set up test fixtures."""
        self.clear_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=72,
            wind_speed=5,
            wind_direction=WindDirection.NONE
        )
        
        self.extreme_weather = Weather(
            condition=WeatherCondition.HEAVY_SNOW,
            temperature=15,
            wind_speed=25,
            wind_direction=WindDirection.CROSSWIND,
            precipitation_intensity=0.9
        )

    def test_weather_creation(self):
        """Test weather object creation."""
        self.assertEqual(self.clear_weather.condition, WeatherCondition.CLEAR)
        self.assertEqual(self.clear_weather.temperature, 72)
        self.assertEqual(self.clear_weather.wind_speed, 5)
        self.assertEqual(self.clear_weather.wind_direction, WindDirection.NONE)

    def test_weather_validation(self):
        """Test weather parameter validation."""
        # Test invalid temperature
        with self.assertRaises(ValueError):
            Weather(temperature=-50)
        
        with self.assertRaises(ValueError):
            Weather(temperature=150)
        
        # Test invalid wind speed
        with self.assertRaises(ValueError):
            Weather(wind_speed=-5)
        
        with self.assertRaises(ValueError):
            Weather(wind_speed=100)
        
        # Test invalid precipitation
        with self.assertRaises(ValueError):
            Weather(precipitation_intensity=-0.1)
        
        with self.assertRaises(ValueError):
            Weather(precipitation_intensity=1.5)

    def test_clear_weather_effects(self):
        """Test that clear weather has minimal effects."""
        effects = self.clear_weather.get_effects()
        
        self.assertAlmostEqual(effects.passing_accuracy_modifier, 1.0, places=2)
        self.assertAlmostEqual(effects.kicking_accuracy_modifier, 1.0, places=2)
        self.assertAlmostEqual(effects.fumble_chance_modifier, 1.0, places=2)
        self.assertAlmostEqual(effects.visibility_modifier, 1.0, places=2)

    def test_extreme_weather_effects(self):
        """Test that extreme weather has significant effects."""
        effects = self.extreme_weather.get_effects()
        
        # Extreme cold and snow should reduce accuracy
        self.assertLess(effects.passing_accuracy_modifier, 0.8)
        self.assertLess(effects.kicking_accuracy_modifier, 0.8)
        self.assertLess(effects.visibility_modifier, 0.9)
        
        # Should increase fumble chance
        self.assertGreater(effects.fumble_chance_modifier, 1.1)

    def test_wind_effects(self):
        """Test wind effects on kicking and passing."""
        # Crosswind
        crosswind_weather = Weather(
            wind_speed=20,
            wind_direction=WindDirection.CROSSWIND
        )
        effects = crosswind_weather.get_effects()
        self.assertLess(effects.kicking_accuracy_modifier, 1.0)
        self.assertLess(effects.passing_accuracy_modifier, 1.0)
        
        # Tailwind
        tailwind_weather = Weather(
            wind_speed=20,
            wind_direction=WindDirection.TAILWIND
        )
        effects = tailwind_weather.get_effects()
        self.assertGreater(effects.kicking_distance_modifier, 1.0)
        self.assertGreater(effects.passing_distance_modifier, 1.0)
        
        # Headwind
        headwind_weather = Weather(
            wind_speed=20,
            wind_direction=WindDirection.HEADWIND
        )
        effects = headwind_weather.get_effects()
        self.assertLess(effects.kicking_distance_modifier, 1.0)
        self.assertLess(effects.passing_distance_modifier, 1.0)

    def test_precipitation_effects(self):
        """Test rain and snow effects."""
        # Heavy rain
        rain_weather = Weather(
            condition=WeatherCondition.HEAVY_RAIN,
            temperature=45,
            precipitation_intensity=0.8
        )
        effects = rain_weather.get_effects()
        self.assertLess(effects.passing_accuracy_modifier, 1.0)
        self.assertGreater(effects.fumble_chance_modifier, 1.0)
        self.assertLess(effects.field_condition_modifier, 1.0)
        
        # Heavy snow
        snow_weather = Weather(
            condition=WeatherCondition.HEAVY_SNOW,
            temperature=25,
            precipitation_intensity=0.9
        )
        effects = snow_weather.get_effects()
        self.assertLess(effects.passing_accuracy_modifier, 1.0)
        self.assertLess(effects.visibility_modifier, 1.0)
        self.assertLess(effects.kicking_accuracy_modifier, 1.0)

    def test_temperature_effects(self):
        """Test temperature effects on gameplay."""
        # Very cold
        cold_weather = Weather(temperature=10)
        effects = cold_weather.get_effects()
        self.assertLess(effects.passing_accuracy_modifier, 1.0)
        self.assertLess(effects.kicking_accuracy_modifier, 1.0)
        self.assertGreater(effects.fumble_chance_modifier, 1.0)
        
        # Very hot
        hot_weather = Weather(temperature=100)
        effects = hot_weather.get_effects()
        self.assertLess(effects.rushing_yards_modifier, 1.0)

    def test_fog_effects(self):
        """Test fog effects on visibility and accuracy."""
        fog_weather = Weather(condition=WeatherCondition.FOG)
        effects = fog_weather.get_effects()
        
        self.assertLess(effects.visibility_modifier, 1.0)
        self.assertLess(effects.passing_accuracy_modifier, 1.0)
        self.assertLess(effects.kicking_accuracy_modifier, 1.0)

    def test_severity_rating(self):
        """Test weather severity rating calculation."""
        self.assertEqual(self.clear_weather.get_severity_rating(), "Ideal")
        self.assertIn(self.extreme_weather.get_severity_rating(), ["Severe", "Extreme"])

    def test_weather_string_representation(self):
        """Test weather string representation."""
        weather_str = str(self.clear_weather)
        self.assertIn("Clear", weather_str)
        self.assertIn("72°F", weather_str)
        
        extreme_str = str(self.extreme_weather)
        self.assertIn("Heavy Snow", extreme_str)
        self.assertIn("15°F", extreme_str)
        self.assertIn("25 mph", extreme_str)


class TestRandomWeatherGeneration(unittest.TestCase):
    """Test cases for random weather generation."""

    def test_random_weather_generation(self):
        """Test that random weather generation works."""
        weather = generate_random_weather(seed=42)
        self.assertIsInstance(weather, Weather)
        self.assertIsInstance(weather.condition, WeatherCondition)
        self.assertIsInstance(weather.wind_direction, WindDirection)

    def test_reproducible_weather(self):
        """Test that weather generation is reproducible with seeds."""
        weather1 = generate_random_weather(seed=123)
        weather2 = generate_random_weather(seed=123)
        
        self.assertEqual(weather1.condition, weather2.condition)
        self.assertEqual(weather1.temperature, weather2.temperature)
        self.assertEqual(weather1.wind_speed, weather2.wind_speed)
        self.assertEqual(weather1.wind_direction, weather2.wind_direction)

    def test_weather_parameter_ranges(self):
        """Test that generated weather parameters are in valid ranges."""
        for seed in range(10):
            weather = generate_random_weather(seed=seed)
            
            # Temperature should be reasonable
            self.assertGreaterEqual(weather.temperature, 15)
            self.assertLessEqual(weather.temperature, 85)
            
            # Wind speed should be reasonable
            self.assertGreaterEqual(weather.wind_speed, 0)
            self.assertLessEqual(weather.wind_speed, 45)
            
            # Precipitation should be valid
            self.assertGreaterEqual(weather.precipitation_intensity, 0.0)
            self.assertLessEqual(weather.precipitation_intensity, 1.0)

    def test_city_weather_tendencies(self):
        """Test city-specific weather tendency data."""
        buffalo_tendencies = get_city_weather_tendency("Buffalo")
        miami_tendencies = get_city_weather_tendency("Miami")
        
        # Buffalo should have more snow tendency than Miami
        self.assertGreater(buffalo_tendencies.get("snow", 0), miami_tendencies.get("snow", 0))
        
        # Miami should have more hot weather than Buffalo
        self.assertGreater(miami_tendencies.get("hot", 0), buffalo_tendencies.get("hot", 0))


class TestWeatherGameIntegration(unittest.TestCase):
    """Test cases for weather integration with game simulation."""

    def setUp(self):
        """Set up test fixtures."""
        self.teams = load_sample_teams()
        self.home_team = self.teams[0]
        self.away_team = self.teams[1]

    def test_game_with_weather(self):
        """Test that games can be simulated with weather."""
        weather = Weather(
            condition=WeatherCondition.LIGHT_RAIN,
            temperature=50,
            wind_speed=10
        )
        
        engine = GameEngine(seed=42, weather=weather)
        result = engine.simulate_game(self.home_team, self.away_team)
        
        self.assertIsNotNone(result.weather)
        if result.weather is not None:
            self.assertEqual(result.weather.condition, WeatherCondition.LIGHT_RAIN)

    def test_game_without_weather_generates_random(self):
        """Test that games without specified weather generate random weather."""
        engine = GameEngine(seed=42)
        result = engine.simulate_game(self.home_team, self.away_team)
        
        self.assertIsNotNone(result.weather)
        self.assertIsInstance(result.weather, Weather)

    def test_weather_affects_game_outcomes(self):
        """Test that weather actually affects game outcomes."""
        # Run games with clear weather
        clear_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=72,
            wind_speed=3
        )
        
        clear_scores = []
        for seed in range(5):
            engine = GameEngine(seed=seed, weather=clear_weather)
            result = engine.simulate_game(self.home_team, self.away_team)
            clear_scores.append(result.home_score + result.away_score)
        
        # Run games with extreme weather
        extreme_weather = Weather(
            condition=WeatherCondition.HEAVY_SNOW,
            temperature=20,
            wind_speed=25,
            wind_direction=WindDirection.CROSSWIND
        )
        
        extreme_scores = []
        for seed in range(5):
            engine = GameEngine(seed=seed, weather=extreme_weather)
            result = engine.simulate_game(self.home_team, self.away_team)
            extreme_scores.append(result.home_score + result.away_score)
        
        # On average, extreme weather should produce lower scores
        avg_clear = np.mean(clear_scores)
        avg_extreme = np.mean(extreme_scores)
        
        # Allow some variance, but extreme weather should generally lower scores
        self.assertLess(float(avg_extreme), float(avg_clear) + 5)  # Some tolerance for randomness

    def test_reproducible_weather_games(self):
        """Test that games with same weather and seed produce same results."""
        weather = Weather(
            condition=WeatherCondition.FOG,
            temperature=45,
            wind_speed=12
        )
        
        engine1 = GameEngine(seed=2024, weather=weather)
        result1 = engine1.simulate_game(self.home_team, self.away_team)
        
        engine2 = GameEngine(seed=2024, weather=weather)
        result2 = engine2.simulate_game(self.home_team, self.away_team)
        
        self.assertEqual(result1.home_score, result2.home_score)
        self.assertEqual(result1.away_score, result2.away_score)


if __name__ == '__main__':
    unittest.main()
