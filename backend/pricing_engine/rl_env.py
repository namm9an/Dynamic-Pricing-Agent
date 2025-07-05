"""Custom Gymnasium environment for dynamic pricing.

This environment uses the trained demand forecasting model when available,
falling back to a simple demand function if the model is not loaded.
"""
from __future__ import annotations

from typing import Any, Tuple, Dict, Optional
from pathlib import Path

import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None

try:
    import gymnasium as gym
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False
    gym = None

try:
    from .demand_model import DemandModel
except (ImportError, OSError):
    DemandModel = None


# Create a base class if gym is not available
if GYM_AVAILABLE:
    BaseEnv = gym.Env
else:
    class BaseEnv:
        def __init__(self):
            pass
        def reset(self):
            raise NotImplementedError
        def step(self, action):
            raise NotImplementedError

class PricingEnv(BaseEnv):
    """Environment that outputs revenue-based rewards for price multipliers."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        base_price: float = 10.0,
        change_penalty: float = 0.1,
        max_steps: int = 50,
        seed: int | None = None,
        use_demand_model: bool = True,
    ) -> None:
        super().__init__()
        self.base_price = base_price
        self.change_penalty = change_penalty
        self.max_steps = max_steps
        self._rng = np.random.default_rng(seed)
        
        # Try to load demand model
        self.demand_model: Optional[DemandModel] = None
        if use_demand_model and DemandModel is not None:
            try:
                self.demand_model = DemandModel()
                if Path("./models/pytorch_model.bin").exists():
                    print("✅ Loaded demand model for RL environment")
                else:
                    self.demand_model = None
                    print("⚠️ Demand model file not found, using fallback")
            except Exception as e:
                print(f"⚠️ Could not load demand model: {e}")
                self.demand_model = None

        # Action: single continuous multiplier 0.8 – 1.5
        if GYM_AVAILABLE:
            self.action_space = gym.spaces.Box(low=np.array([0.8], dtype=np.float32),
                                               high=np.array([1.5], dtype=np.float32),
                                               dtype=np.float32)

            # Observation: [predicted_demand, last_price_multiplier]
            self.observation_space = gym.spaces.Box(
                low=np.array([0.0, 0.8], dtype=np.float32),
                high=np.array([np.finfo(np.float32).max, 1.5], dtype=np.float32),
                dtype=np.float32,
            )
        else:
            # Simple fallback for when gym is not available
            self.action_space = None
            self.observation_space = None

        self._step_idx: int = 0
        self._last_multiplier: float = 1.0  # start at base_price
        self._demand_forecast: float = 1.0

    # ---------------------------------------------------------------------
    # Gymnasium required methods
    # ---------------------------------------------------------------------

    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._step_idx = 0
        self._last_multiplier = 1.0
        self._demand_forecast = self._simulate_demand(self._last_multiplier)
        obs = np.array([self._demand_forecast, self._last_multiplier], dtype=np.float32)
        info: Dict[str, Any] = {}
        return obs, info

    def step(self, action: np.ndarray):
        self._step_idx += 1
        multiplier = float(action[0].clip(0.8, 1.5))
        price = self.base_price * multiplier

        # Predict demand (placeholder simulation)
        demand = self._simulate_demand(multiplier)
        revenue = price * demand

        price_change_penalty = abs(multiplier - self._last_multiplier) * self.change_penalty
        reward = revenue - price_change_penalty

        # Update state
        self._last_multiplier = multiplier
        self._demand_forecast = demand
        obs = np.array([self._demand_forecast, self._last_multiplier], dtype=np.float32)

        done = self._step_idx >= self.max_steps
        truncated = False
        info: Dict[str, Any] = {
            "price": price,
            "demand": demand,
            "revenue": revenue,
            "penalty": price_change_penalty,
        }
        return obs, reward, done, truncated, info

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------

    def _simulate_demand(self, multiplier: float) -> float:
        """Predict demand using ML model or fallback to simple simulation.
        
        Uses the trained demand model if available, otherwise falls back
        to a simple inverse-price demand curve.
        """
        price = self.base_price * multiplier
        
        # Try to use the demand model first
        if self.demand_model is not None:
            try:
                # Create a simple feature sequence for the model
                # Features: [price, units_sold, is_holiday, weather_code]
                # We'll use simplified assumptions for the RL environment
                features = [
                    [price, 50, 0, 1],  # Day 1
                    [price, 48, 0, 1],  # Day 2
                    [price, 52, 0, 2],  # Day 3
                    [price, 49, 0, 1],  # Day 4
                    [price, 51, 0, 1],  # Day 5
                    [price, 50, 0, 2],  # Day 6
                    [price, 50, 0, 1],  # Day 7 (prediction day)
                ]
                
                if TORCH_AVAILABLE:
                    input_tensor = torch.tensor([features], dtype=torch.float32)
                    with torch.no_grad():
                        prediction = self.demand_model.predict(input_tensor)
                        if prediction is not None:
                            return float(max(0.1, prediction[0]))
            except Exception as e:
                # Fall back to simple model on any error
                pass
        
        # Fallback: Simple inverse-price demand curve
        baseline = max(0.1, 2.0 - price * 0.05)
        noise = self._rng.normal(0, 0.05)
        return float(max(0.0, baseline + noise))
