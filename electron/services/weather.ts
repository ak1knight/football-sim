export enum WeatherCondition {
  CLEAR = 'Clear',
  CLOUDY = 'Cloudy',
  LIGHT_RAIN = 'Light Rain',
  HEAVY_RAIN = 'Heavy Rain',
  LIGHT_SNOW = 'Light Snow',
  HEAVY_SNOW = 'Heavy Snow',
  FOG = 'Fog',
}

export enum WindDirection {
  NONE = 'Calm',
  CROSSWIND = 'Crosswind',
  HEADWIND = 'Headwind',
  TAILWIND = 'Tailwind',
}

export interface WeatherEffects {
  passing_accuracy_modifier: number;
  passing_distance_modifier: number;
  kicking_accuracy_modifier: number;
  kicking_distance_modifier: number;
  rushing_yards_modifier: number;
  fumble_chance_modifier: number;
  visibility_modifier: number;
  field_condition_modifier: number;
}

export interface Weather {
  condition: WeatherCondition;
  temperature: number;
  wind_speed: number;
  wind_direction: WindDirection;
  precipitation_intensity: number;
}

export function defaultWeatherEffects(): WeatherEffects {
  return {
    passing_accuracy_modifier: 1,
    passing_distance_modifier: 1,
    kicking_accuracy_modifier: 1,
    kicking_distance_modifier: 1,
    rushing_yards_modifier: 1,
    fumble_chance_modifier: 1,
    visibility_modifier: 1,
    field_condition_modifier: 1,
  };
}

export function weatherToString(weather: Weather): string {
  const wind = weather.wind_speed > 5 ? `, ${weather.wind_speed} mph ${weather.wind_direction}` : '';
  return `${weather.condition}, ${weather.temperature}°F${wind}`;
}

export function getWeatherEffects(weather: Weather): WeatherEffects {
  const effects = defaultWeatherEffects();

  if (weather.temperature < 20) {
    effects.passing_accuracy_modifier *= 0.85;
    effects.kicking_accuracy_modifier *= 0.8;
    effects.fumble_chance_modifier *= 1.25;
  } else if (weather.temperature < 32) {
    effects.passing_accuracy_modifier *= 0.92;
    effects.kicking_accuracy_modifier *= 0.88;
    effects.fumble_chance_modifier *= 1.15;
  } else if (weather.temperature > 95) {
    effects.rushing_yards_modifier *= 0.95;
    effects.field_condition_modifier *= 0.98;
  }

  if (weather.wind_speed > 10) {
    const windFactor = Math.min(weather.wind_speed / 30, 1);
    if (weather.wind_direction === WindDirection.CROSSWIND) {
      effects.kicking_accuracy_modifier *= 1 - windFactor * 0.2;
      effects.passing_accuracy_modifier *= 1 - windFactor * 0.15;
    } else if (weather.wind_direction === WindDirection.HEADWIND) {
      effects.kicking_distance_modifier *= 1 - windFactor * 0.25;
      effects.passing_distance_modifier *= 1 - windFactor * 0.2;
    } else if (weather.wind_direction === WindDirection.TAILWIND) {
      effects.kicking_distance_modifier *= 1 + windFactor * 0.15;
      effects.passing_distance_modifier *= 1 + windFactor * 0.1;
    }
  }

  if (weather.condition === WeatherCondition.LIGHT_RAIN || weather.condition === WeatherCondition.HEAVY_RAIN) {
    const factor = weather.condition === WeatherCondition.LIGHT_RAIN ? 0.3 : 0.6;
    effects.passing_accuracy_modifier *= 1 - factor * 0.15;
    effects.fumble_chance_modifier *= 1 + factor * 0.25;
    effects.kicking_accuracy_modifier *= 1 - factor * 0.12;
    effects.field_condition_modifier *= 1 - factor * 0.2;
  } else if (weather.condition === WeatherCondition.LIGHT_SNOW || weather.condition === WeatherCondition.HEAVY_SNOW) {
    const factor = weather.condition === WeatherCondition.LIGHT_SNOW ? 0.4 : 0.8;
    effects.passing_accuracy_modifier *= 1 - factor * 0.2;
    effects.visibility_modifier *= 1 - factor * 0.15;
    effects.kicking_accuracy_modifier *= 1 - factor * 0.18;
    effects.field_condition_modifier *= 1 - factor * 0.25;
    effects.rushing_yards_modifier *= 1 - factor * 0.1;
  } else if (weather.condition === WeatherCondition.FOG) {
    effects.visibility_modifier *= 0.85;
    effects.passing_accuracy_modifier *= 0.9;
    effects.kicking_accuracy_modifier *= 0.92;
  }

  return effects;
}

export function generateRandomWeather(seed?: number): Weather {
  const rng = seed !== undefined ? seededRandom(seed) : Math.random;
  const roll = rng();
  const conditions: Array<{ condition: WeatherCondition; weight: number }> = [
    { condition: WeatherCondition.CLEAR, weight: 0.35 },
    { condition: WeatherCondition.CLOUDY, weight: 0.25 },
    { condition: WeatherCondition.LIGHT_RAIN, weight: 0.15 },
    { condition: WeatherCondition.HEAVY_RAIN, weight: 0.08 },
    { condition: WeatherCondition.LIGHT_SNOW, weight: 0.1 },
    { condition: WeatherCondition.HEAVY_SNOW, weight: 0.04 },
    { condition: WeatherCondition.FOG, weight: 0.03 },
  ];

  let cumulative = 0;
  let chosen = WeatherCondition.CLEAR;
  for (const entry of conditions) {
    cumulative += entry.weight;
    if (roll <= cumulative) {
      chosen = entry.condition;
      break;
    }
  }

  let temperature = 70;
  if (chosen === WeatherCondition.LIGHT_SNOW || chosen === WeatherCondition.HEAVY_SNOW) {
    temperature = Math.floor(15 + rng() * 20);
  } else if (chosen === WeatherCondition.LIGHT_RAIN || chosen === WeatherCondition.HEAVY_RAIN) {
    temperature = Math.floor(35 + rng() * 40);
  } else {
    temperature = Math.floor(25 + rng() * 60);
  }

  const wind_speed = Math.min(45, Math.max(0, Math.floor(normal(rng, 8, 6))));
  const wind_direction =
    wind_speed > 5
      ? [WindDirection.CROSSWIND, WindDirection.HEADWIND, WindDirection.TAILWIND][Math.floor(rng() * 3)]
      : WindDirection.NONE;

  let precipitation_intensity = 0;
  if (chosen === WeatherCondition.LIGHT_RAIN || chosen === WeatherCondition.LIGHT_SNOW) {
    precipitation_intensity = 0.2 + rng() * 0.3;
  } else if (chosen === WeatherCondition.HEAVY_RAIN || chosen === WeatherCondition.HEAVY_SNOW) {
    precipitation_intensity = 0.6 + rng() * 0.4;
  }

  return {
    condition: chosen,
    temperature,
    wind_speed,
    wind_direction,
    precipitation_intensity,
  };
}

function seededRandom(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
}

function normal(rng: () => number, mean: number, std: number): number {
  let u = 0;
  let v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  const mag = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return mean + std * mag;
}
