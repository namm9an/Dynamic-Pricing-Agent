#!/usr/bin/env python3
"""Train a robust pricing agent that works with our current setup."""

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
    SB3_AVAILABLE = True
    print("✅ SB3 and Gymnasium available")
except ImportError as e:
    print(f"❌ SB3/Gym not available: {e}")
    exit(1)

from pricing_engine.rl_env import PricingEnv

def train_robust_agent():
    """Train a robust PPO agent that can be properly saved and loaded."""
    
    print("🚀 Training robust PPO agent...")
    
    # Create environment
    env = PricingEnv(base_price=10.0, max_steps=50, use_demand_model=False)
    
    # Check environment
    try:
        check_env(env)
        print("✅ Environment passed checks")
    except Exception as e:
        print(f"⚠️ Environment check warning: {e}")
    
    # Create PPO model with stable configuration
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        seed=42,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        device='cpu'  # Force CPU to avoid CUDA issues
    )
    
    print("🏋️ Training for 10,000 timesteps...")
    model.learn(total_timesteps=10_000)
    
    # Test the trained model
    print("\n🧪 Testing trained model...")
    obs, _ = env.reset()
    total_reward = 0
    prices = []
    
    for i in range(10):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        prices.append(info['price'])
        print(f"  Step {i+1}: Price=${info['price']:.2f}, Demand={info['demand']:.2f}, Revenue=${info['revenue']:.2f}")
        
        if done or truncated:
            break
    
    print(f"\n📊 Test Results:")
    print(f"  Total reward: {total_reward:.2f}")
    print(f"  Average price: ${np.mean(prices):.2f}")
    print(f"  Price stability: {np.std(prices):.2f}")
    
    # Save the model properly
    project_root = Path(__file__).parent.parent
    model_dir = project_root / "models" / "pricing_agent"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "ppo_pricing_robust.zip"
    model.save(str(model_path))
    print(f"✅ Model saved to {model_path}")
    
    # Save training stats
    stats = {
        "algorithm": "PPO",
        "total_timesteps": 10_000,
        "test_reward": total_reward,
        "test_avg_price": float(np.mean(prices)),
        "test_price_std": float(np.std(prices)),
        "model_path": str(model_path)
    }
    
    stats_path = model_dir / "robust_training_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Training stats saved to {stats_path}")
    
    # Test loading the saved model
    print("\n🔄 Testing model loading...")
    try:
        loaded_model = PPO.load(str(model_path), env=env)
        obs, _ = env.reset()
        action, _ = loaded_model.predict(obs, deterministic=True)
        print(f"✅ Model loaded successfully! Predicted action: {action}")
        
        # Create a simple wrapper that works with our existing code
        import pickle
        
        class RobustPPOWrapper:
            def __init__(self, model_path, env):
                self.model = PPO.load(str(model_path), env=env)
                self.env = env
            
            def predict(self, obs, deterministic=True):
                return self.model.predict(obs, deterministic=deterministic)
        
        # Save the wrapper
        wrapper = RobustPPOWrapper(model_path, env)
        wrapper_data = {
            'agent': wrapper,
            'type': 'robust_ppo',
            'model_path': str(model_path),
            'stats': stats
        }
        
        # Instead of saving the wrapper with model, let's create a simpler solution
        # Create a prediction function that can be pickled
        def create_predictor():
            from stable_baselines3 import PPO
            from pricing_engine.rl_env import PricingEnv
            
            env = PricingEnv(base_price=10.0)
            model_path = model_dir / "ppo_pricing_robust.zip"
            model = PPO.load(str(model_path), env=env)
            
            def predict(obs, deterministic=True):
                return model.predict(obs, deterministic=deterministic)
            
            return predict, model
        
        # Save a simple reference
        simple_data = {
            'type': 'robust_ppo_reference',
            'model_path': str(model_path),
            'stats': stats,
            'creation_function': 'create_predictor'
        }
        
        simple_path = model_dir / "ppo_pricing.pkl"
        with open(simple_path, 'wb') as f:
            pickle.dump(simple_data, f)
        print(f"✅ Simple reference saved to {simple_path}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None

if __name__ == "__main__":
    stats = train_robust_agent()
    if stats:
        print("\n🎯 Robust agent training completed successfully!")
        print(f"📈 Final test reward: {stats['test_reward']:.2f}")
    else:
        print("❌ Training failed!")
