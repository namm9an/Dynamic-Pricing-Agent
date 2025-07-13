#!/usr/bin/env python3
"""Train an optimized pricing agent that achieves better revenue lift."""

import sys
import os
import json
from pathlib import Path
import numpy as np

# Add D:\PythonPackages to sys.path for dependencies
if "D:\\PythonPackages" not in sys.path:
    sys.path.insert(0, "D:\\PythonPackages")

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = "D:\\PythonPackages" + os.pathsep + os.environ.get('PYTHONPATH', '')

sys.path.append(str(Path(__file__).parent))

try:
    import gymnasium as gym
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_checker import check_env
    from stable_baselines3.common.callbacks import EvalCallback
    SB3_AVAILABLE = True
    print("✅ SB3 and Gymnasium available")
except ImportError as e:
    print(f"❌ SB3/Gym not available: {e}")
    exit(1)

from pricing_engine.rl_env import PricingEnv

class OptimizedPricingEnv(PricingEnv):
    """Enhanced pricing environment with better reward shaping."""
    
    def __init__(self, base_price=10.0, change_penalty=0.05, max_steps=50):
        super().__init__(base_price, change_penalty, max_steps, use_demand_model=False)
        self.baseline_revenue = base_price * 1.0  # Baseline at neutral demand
        
    def step(self, action):
        obs, reward, done, truncated, info = super().step(action)
        
        # Enhanced reward shaping
        price = info["price"]
        demand = info["demand"]
        revenue = info["revenue"]
        
        # Calculate revenue lift compared to baseline
        revenue_lift = (revenue - self.baseline_revenue) / self.baseline_revenue
        
        # Reward based on revenue improvement
        reward = revenue + revenue_lift * 50  # Bonus for beating baseline
        
        # Penalty for extreme prices
        multiplier = price / self.base_price
        if multiplier < 0.85 or multiplier > 1.4:
            reward -= 20
        
        # Update info
        info["enhanced_reward"] = reward
        info["revenue_lift"] = revenue_lift
        
        return obs, reward, done, truncated, info

def train_optimized_agent():
    """Train an optimized PPO agent with better reward shaping."""
    
    print("🚀 Training optimized PPO agent...")
    
    # Create enhanced environment
    env = OptimizedPricingEnv(base_price=10.0, change_penalty=0.05)
    eval_env = OptimizedPricingEnv(base_price=10.0, change_penalty=0.05)
    
    # Check environment
    try:
        check_env(env)
        print("✅ Environment passed checks")
    except Exception as e:
        print(f"⚠️ Environment check warning: {e}")
    
    # Create PPO model with optimized hyperparameters
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        seed=42,
        learning_rate=0.001,  # Higher learning rate
        n_steps=4096,  # More steps per update
        batch_size=128,  # Larger batch size
        n_epochs=10,
        gamma=0.95,  # Slightly less future-focused
        gae_lambda=0.9,
        clip_range=0.3,  # More aggressive updates
        ent_coef=0.01,  # More exploration
        device='cpu'
    )
    
    # Setup evaluation callback
    project_root = Path(__file__).parent.parent
    model_dir = project_root / "models" / "pricing_agent"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir),
        log_path=str(model_dir),
        eval_freq=2000,
        deterministic=True,
        render=False
    )
    
    print("🏋️ Training for 20,000 timesteps...")
    model.learn(total_timesteps=20_000, callback=eval_callback)
    
    # Test different scenarios
    print("\n🧪 Testing trained model on various scenarios...")
    
    scenarios = [
        (0.5, "Low demand"),
        (1.0, "Normal demand"), 
        (1.5, "High demand"),
        (2.0, "Very high demand")
    ]
    
    results = []
    for demand, desc in scenarios:
        obs = np.array([demand, 1.0], dtype=np.float32)
        action, _ = model.predict(obs, deterministic=True)
        multiplier = float(action[0])
        price = 10.0 * multiplier
        revenue = price * demand
        
        print(f"  {desc}: Demand={demand:.1f} → Multiplier={multiplier:.3f}, Price=${price:.2f}, Revenue=${revenue:.2f}")
        results.append({
            "demand": demand,
            "multiplier": multiplier,
            "price": price,
            "revenue": revenue,
            "description": desc
        })
    
    # Calculate performance metrics
    baseline_revenues = [10.0 * demand for demand, _ in scenarios]
    actual_revenues = [r["revenue"] for r in results]
    total_baseline = sum(baseline_revenues)
    total_actual = sum(actual_revenues)
    revenue_lift = (total_actual - total_baseline) / total_baseline * 100
    
    print(f"\n📊 Performance Summary:")
    print(f"  Total baseline revenue: ${total_baseline:.2f}")
    print(f"  Total optimized revenue: ${total_actual:.2f}")
    print(f"  Revenue lift: {revenue_lift:.1f}%")
    
    # Save the model
    model_path = model_dir / "ppo_pricing_optimized.zip"
    model.save(str(model_path))
    print(f"✅ Model saved to {model_path}")
    
    # Save training stats
    stats = {
        "algorithm": "PPO_Optimized",
        "total_timesteps": 20_000,
        "revenue_lift_pct": revenue_lift,
        "scenario_results": results,
        "model_path": str(model_path)
    }
    
    stats_path = model_dir / "optimized_training_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Training stats saved to {stats_path}")
    
    # Create the reference for loading
    if revenue_lift > 3:  # Only use if it's better than current
        reference_data = {
            'type': 'robust_ppo_reference',
            'model_path': str(model_path),
            'stats': stats,
            'optimized': True
        }
        
        reference_path = model_dir / "ppo_pricing.pkl"
        import pickle
        with open(reference_path, 'wb') as f:
            pickle.dump(reference_data, f)
        print(f"✅ Updated model reference to optimized version")
        
        return stats
    else:
        print("⚠️ Optimized model didn't meet improvement threshold, keeping existing model")
        return None

async def train_rl_agent(
    existing_agent_path=None,
    env_config=None,
    total_timesteps=50000,
    learning_rate=0.0001
):
    """Train RL agent with given configuration."""
    print("🚀 Training RL agent...")
    
    # Create environment
    env = OptimizedPricingEnv(base_price=10.0, change_penalty=0.05)
    
    # Create or load model
    if existing_agent_path and os.path.exists(existing_agent_path):
        try:
            model = PPO.load(existing_agent_path, env=env)
            print(f"✅ Loaded existing agent from {existing_agent_path}")
        except Exception as e:
            print(f"⚠️ Could not load existing agent: {e}")
            model = PPO(
                "MlpPolicy",
                env,
                verbose=0,
                learning_rate=learning_rate,
                device='cpu'
            )
    else:
        model = PPO(
            "MlpPolicy",
            env,
            verbose=0,
            learning_rate=learning_rate,
            device='cpu'
        )
    
    # Train the model
    print(f"🏋️ Training for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)
    
    print("✅ RL agent training completed")
    return model

if __name__ == "__main__":
    stats = train_optimized_agent()
    if stats:
        print(f"\n🎯 Optimized agent training completed successfully!")
        print(f"📈 Revenue lift achieved: {stats['revenue_lift_pct']:.1f}%")
    else:
        print("❌ Optimization failed to improve performance!")
