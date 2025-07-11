"""
Weather model for the football simulation.

This module defines weather conditions and their effects on gameplay,
including precipitation, wind, and temperature impacts.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional


class WeatherCondition(Enum):
    """Weather condition types."""
    CLEAR = "Clear"
    CLOUDY = "Cloudy"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"
    LIGHT_SNOW = "Light Snow"
    HEAVY_SNOW = "Heavy Snow"
    FOG = "Fog"


class WindDirection(Enum):
    """Wind direction relative to field."""
    NONE = "Calm"
    CROSSWIND = "Crosswind"
    HEADWIND = "Headwind"
    TAILWIND = "Tailwind"


@dataclass
class WeatherEffects:
    """Weather effects on gameplay statistics."""
    # Passing effects (multipliers, 1.0 = no effect)
    passing_accuracy_modifier: float = 1.0
    passing_distance_modifier: float = 1.0
    
    # Kicking effects
    kicking_accuracy_modifier: float = 1.0
    kicking_distance_modifier: float = 1.0
    
    # Rushing effects
    rushing_yards_modifier: float = 1.0
    fumble_chance_modifier: float = 1.0
    
    # General effects
    visibility_modifier: float = 1.0  # Affects all skills
    field_condition_modifier: float = 1.0  # Affects footing and cuts


@dataclass
class Weather:
    """
    Represents weather conditions during a football game.
    """
    condition: WeatherCondition = WeatherCondition.CLEAR
    temperature: int = 72  # Fahrenheit
    wind_speed: int = 0    # MPH
    wind_direction: WindDirection = WindDirection.NONE
    precipitation_intensity: float = 0.0  # 0.0 to 1.0
    
    def __post_init__(self):
        """Validate weather data after initialization."""
        if not -20 <= self.temperature <= 120:
            raise ValueError("Temperature must be between -20°F and 120°F")
        
        if not 0 <= self.wind_speed <= 60:
            raise ValueError("Wind speed must be between 0 and 60 MPH")
            
        if not 0.0 <= self.precipitation_intensity <= 1.0:
            raise ValueError("Precipitation intensity must be between 0.0 and 1.0")
    
    def get_effects(self) -> WeatherEffects:
        """Calculate weather effects on gameplay."""
        effects = WeatherEffects()
        
        # Temperature effects
        if self.temperature < 32:  # Freezing
            effects.passing_accuracy_modifier *= 0.92
            effects.kicking_accuracy_modifier *= 0.88
            effects.fumble_chance_modifier *= 1.15
        elif self.temperature < 20:  # Extremely cold
            effects.passing_accuracy_modifier *= 0.85
            effects.kicking_accuracy_modifier *= 0.80
            effects.fumble_chance_modifier *= 1.25
        elif self.temperature > 95:  # Very hot
            effects.rushing_yards_modifier *= 0.95
            effects.field_condition_modifier *= 0.98
        
        # Wind effects
        if self.wind_speed > 10:
            wind_factor = min(self.wind_speed / 30.0, 1.0)
            
            if self.wind_direction == WindDirection.CROSSWIND:
                effects.kicking_accuracy_modifier *= (1.0 - wind_factor * 0.2)
                effects.passing_accuracy_modifier *= (1.0 - wind_factor * 0.15)
            elif self.wind_direction == WindDirection.HEADWIND:
                effects.kicking_distance_modifier *= (1.0 - wind_factor * 0.25)
                effects.passing_distance_modifier *= (1.0 - wind_factor * 0.20)
            elif self.wind_direction == WindDirection.TAILWIND:
                effects.kicking_distance_modifier *= (1.0 + wind_factor * 0.15)
                effects.passing_distance_modifier *= (1.0 + wind_factor * 0.10)
        
        # Precipitation effects
        if self.condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.HEAVY_RAIN]:
            rain_factor = 0.3 if self.condition == WeatherCondition.LIGHT_RAIN else 0.6
            effects.passing_accuracy_modifier *= (1.0 - rain_factor * 0.15)
            effects.fumble_chance_modifier *= (1.0 + rain_factor * 0.25)
            effects.kicking_accuracy_modifier *= (1.0 - rain_factor * 0.12)
            effects.field_condition_modifier *= (1.0 - rain_factor * 0.20)
        
        elif self.condition in [WeatherCondition.LIGHT_SNOW, WeatherCondition.HEAVY_SNOW]:
            snow_factor = 0.4 if self.condition == WeatherCondition.LIGHT_SNOW else 0.8
            effects.passing_accuracy_modifier *= (1.0 - snow_factor * 0.20)
            effects.visibility_modifier *= (1.0 - snow_factor * 0.15)
            effects.kicking_accuracy_modifier *= (1.0 - snow_factor * 0.18)
            effects.field_condition_modifier *= (1.0 - snow_factor * 0.25)
            effects.rushing_yards_modifier *= (1.0 - snow_factor * 0.10)
        
        elif self.condition == WeatherCondition.FOG:
            effects.visibility_modifier *= 0.85
            effects.passing_accuracy_modifier *= 0.90
            effects.kicking_accuracy_modifier *= 0.92
        
        return effects
    
    def get_severity_rating(self) -> str:
        """Get a human-readable severity rating for the weather."""
        severity_score = 0
        
        # Temperature severity
        if self.temperature < 20 or self.temperature > 100:
            severity_score += 3
        elif self.temperature < 32 or self.temperature > 90:
            severity_score += 2
        elif self.temperature < 40 or self.temperature > 85:
            severity_score += 1
        
        # Wind severity
        if self.wind_speed > 25:
            severity_score += 3
        elif self.wind_speed > 15:
            severity_score += 2
        elif self.wind_speed > 8:
            severity_score += 1
        
        # Precipitation severity
        if self.condition in [WeatherCondition.HEAVY_RAIN, WeatherCondition.HEAVY_SNOW]:
            severity_score += 3
        elif self.condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.LIGHT_SNOW]:
            severity_score += 2
        elif self.condition == WeatherCondition.FOG:
            severity_score += 1
        
        if severity_score >= 7:
            return "Extreme"
        elif severity_score >= 5:
            return "Severe"
        elif severity_score >= 3:
            return "Moderate"
        elif severity_score >= 1:
            return "Mild"
        else:
            return "Ideal"
    
    def __str__(self) -> str:
        """String representation of weather conditions."""
        wind_str = ""
        if self.wind_speed > 5:
            wind_str = f", {self.wind_speed} mph {self.wind_direction.value} wind"
        
        return f"{self.condition.value}, {self.temperature}°F{wind_str}"


def generate_random_weather(seed: Optional[int] = None) -> Weather:
    """
    Generate random weather conditions based on realistic distributions.
    
    Args:
        seed: Optional random seed for reproducible weather
        
    Returns:
        Weather object with random conditions
    """
    if seed is not None:
        random.seed(seed)
    
    # Weather condition probabilities (roughly based on NFL season averages)
    conditions = [
        (WeatherCondition.CLEAR, 0.35),
        (WeatherCondition.CLOUDY, 0.25),
        (WeatherCondition.LIGHT_RAIN, 0.15),
        (WeatherCondition.HEAVY_RAIN, 0.08),
        (WeatherCondition.LIGHT_SNOW, 0.10),
        (WeatherCondition.HEAVY_SNOW, 0.04),
        (WeatherCondition.FOG, 0.03),
    ]
    
    # Select condition based on weighted probability
    rand_val = random.random()
    cumulative = 0.0
    condition = WeatherCondition.CLEAR
    
    for cond, prob in conditions:
        cumulative += prob
        if rand_val <= cumulative:
            condition = cond
            break
    
    # Generate temperature based on condition and season
    if condition in [WeatherCondition.LIGHT_SNOW, WeatherCondition.HEAVY_SNOW]:
        temperature = random.randint(15, 35)
    elif condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.HEAVY_RAIN]:
        temperature = random.randint(35, 75)
    else:
        temperature = random.randint(25, 85)
    
    # Generate wind
    wind_speed = max(0, int(random.normalvariate(8, 6)))
    wind_speed = min(wind_speed, 45)  # Cap at reasonable maximum
    
    wind_direction = WindDirection.NONE
    if wind_speed > 5:
        wind_directions = [WindDirection.CROSSWIND, WindDirection.HEADWIND, WindDirection.TAILWIND]
        wind_direction = random.choice(wind_directions)
    
    # Generate precipitation intensity
    precipitation = 0.0
    if condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.LIGHT_SNOW]:
        precipitation = random.uniform(0.2, 0.5)
    elif condition in [WeatherCondition.HEAVY_RAIN, WeatherCondition.HEAVY_SNOW]:
        precipitation = random.uniform(0.6, 1.0)
    
    return Weather(
        condition=condition,
        temperature=temperature,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        precipitation_intensity=precipitation
    )


def get_city_weather_tendency(city: str) -> Dict[str, float]:
    """
    Get weather tendencies for specific NFL cities.
    Returns probabilities for different weather conditions.
    """
    # Weather tendencies by city (simplified for demonstration)
    city_weather = {
        "Buffalo": {"snow": 0.25, "cold": 0.4, "rain": 0.2},
        "Green Bay": {"snow": 0.20, "cold": 0.35, "rain": 0.15},
        "Chicago": {"snow": 0.18, "cold": 0.30, "rain": 0.18},
        "Cleveland": {"snow": 0.15, "cold": 0.25, "rain": 0.22},
        "Pittsburgh": {"snow": 0.12, "cold": 0.25, "rain": 0.20},
        "New England": {"snow": 0.15, "cold": 0.30, "rain": 0.18},
        "Denver": {"snow": 0.20, "cold": 0.25, "wind": 0.30},
        "Seattle": {"rain": 0.40, "cloudy": 0.30},
        "Miami": {"hot": 0.35, "rain": 0.25},
        "Tampa Bay": {"hot": 0.30, "rain": 0.20},
        "Arizona": {"hot": 0.40, "clear": 0.50},
        "Las Vegas": {"hot": 0.35, "clear": 0.45},
        "Los Angeles": {"clear": 0.60, "mild": 0.30},
        "San Francisco": {"fog": 0.15, "mild": 0.40},
    }
    
    return city_weather.get(city, {"clear": 0.50, "mild": 0.30})
