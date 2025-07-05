from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, Any, Union

import numpy as np

# Try to import SB3 but don't fail if it's not available
SB3_AVAILABLE = False
try:
    import gymnasium as gym
    from stable_baselines3 import PPO
    SB3_AVAILABLE = True
except (ImportError, OSError) as e:
    # Handle both import errors and DLL loading errors
    print(f"⚠️ Stable-baselines3 not available: {e}")
    gym = None
    PPO = None

from .rl_env import PricingEnv

# Get the project root directory (parent of backend)
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "pricing_agent"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH_PKL = MODEL_DIR / "ppo_pricing.pkl"
MODEL_PATH_ZIP = MODEL_DIR / "ppo_pricing.zip"


def train(env: gym.Env | None = None, timesteps: int = 10_000):
    """Train a PPO agent on the provided environment."""
    if env is None:
        # Create a default environment for quick CLI training
        env = PricingEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=timesteps)
    model.save(MODEL_PATH_ZIP.as_posix())
    return model


def load() -> Union[object, None]:
    """Load a trained PPO agent if exists, else raise FileNotFoundError."""
    
    # Try to load pickle file first (our simplified agent)
    if MODEL_PATH_PKL.exists():
        try:
            with open(MODEL_PATH_PKL, 'rb') as f:
                data = pickle.load(f)
                
                # Handle different pickle formats
                if isinstance(data, dict):
                    if 'agent' in data:
                        print("✅ Loaded simplified PPO agent")
                        return data['agent']
                    elif data.get('type') == 'robust_ppo_reference':
                        # Load the referenced SB3 model
                        model_path = data['model_path']
                        try:
                            from .rl_env import PricingEnv
                            env = PricingEnv()
                            model = PPO.load(model_path, env=env)
                            print("✅ Loaded robust PPO model via reference")
                            return model
                        except Exception as ref_error:
                            print(f"Failed to load referenced model: {ref_error}")
                            
                print("✅ Loaded pickle model")
                return data
        except Exception as pickle_error:
            print(f"Failed to load pickle: {pickle_error}")
    
    # Try to load SB3 zip file as fallback
    if MODEL_PATH_ZIP.exists() and SB3_AVAILABLE:
        try:
            # Import PricingEnv to provide the spaces for loading
            from .rl_env import PricingEnv
            env = PricingEnv()
            
            # Load with custom objects to handle spaces compatibility
            model = PPO.load(MODEL_PATH_ZIP.as_posix(), env=env)
            print("✅ Loaded SB3 PPO model")
            return model
        except Exception as e:
            print(f"Failed to load SB3 model: {e}")
    
    # If no models found
    if not MODEL_PATH_PKL.exists() and not MODEL_PATH_ZIP.exists():
        raise FileNotFoundError("No trained model found. Run train() first.")
    
    raise FileNotFoundError(f"Could not load model from available files")


def recommend_price(
    demand_forecast: float,
    last_multiplier: float = 1.0,
    base_price: float = 10.0,
) -> Dict[str, Any]:
    """Return optimal price and expected revenue given demand forecast.

    This helper wraps the PPO agent (either SB3 or simplified version).
    Falls back to a heuristic approach if no model is available.
    """
    
    # Try to load and use trained model
    try:
        model = load()
        obs = np.array([demand_forecast, last_multiplier], dtype=np.float32)
        
        # Handle different model types
        if hasattr(model, 'predict'):
            # SB3 model or simplified agent with predict method
            if SB3_AVAILABLE and isinstance(model, PPO):
                # Standard SB3 model
                obs_2d = obs.reshape(1, -1)
                action, _states = model.predict(obs_2d, deterministic=True)
                multiplier = float(action[0])
            else:
                # Simplified agent
                action, _ = model.predict(obs, deterministic=True)
                multiplier = float(action[0])
        else:
            # Model loaded but doesn't have predict method
            multiplier = _get_heuristic_multiplier(demand_forecast)
            
    except (FileNotFoundError, Exception) as e:
        # No model available or loading failed - use heuristic
        print(f"⚠️ Using heuristic pricing (model unavailable): {e}")
        multiplier = _get_heuristic_multiplier(demand_forecast)
    
    multiplier = float(np.clip(multiplier, 0.8, 1.5))
    optimal_price = base_price * multiplier
    expected_revenue = optimal_price * demand_forecast
    return {
        "multiplier": multiplier,
        "optimal_price": round(optimal_price, 2),
        "expected_revenue": round(expected_revenue, 2),
        "model_type": "heuristic" if "heuristic" in str(locals().get('e', '')) else "ml"
    }


def _get_heuristic_multiplier(demand_forecast: float) -> float:
    """Get price multiplier using simple heuristic rules."""
    if demand_forecast > 1.5:
        return 0.95  # Lower price for high demand (increase volume)
    elif demand_forecast < 0.5:
        return 1.25  # Higher price for low demand (maintain margin)
    elif demand_forecast > 1.0:
        return 0.98  # Slightly lower for above-average demand
    else:
        return 1.05  # Slightly higher for below-average demand
