"""CLI script to train the PPO pricing agent.

Usage:

    python backend/train_pricing_agent_fixed.py --steps 20000 --base_price 12

The script will save the trained model under `models/pricing_agent/ppo_pricing.zip`.
"""
from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path as _Path

# Add D:\PythonPackages to sys.path for dependencies
if "D:\\PythonPackages" not in sys.path:
    sys.path.insert(0, "D:\\PythonPackages")

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = "D:\\PythonPackages" + os.pathsep + os.environ.get('PYTHONPATH', '')

# Ensure the backend directory is on PYTHONPATH when running as a script
ROOT_DIR = _Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
from pathlib import Path

try:
    import gymnasium as gym
    from stable_baselines3 import PPO
    print("✅ Successfully imported gymnasium and stable-baselines3")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure dependencies are installed in D:\\PythonPackages")
    sys.exit(1)

from pricing_engine.rl_env import PricingEnv
from pricing_engine.rl_agent import MODEL_PATH


def parse_args():
    parser = argparse.ArgumentParser(description="Train PPO pricing agent")
    parser.add_argument("--steps", type=int, default=10_000, help="Training steps")
    parser.add_argument("--base_price", type=float, default=10.0, help="Base product price")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()
    
    print(f"🚀 Starting PPO training with {args.steps} steps...")
    print(f"Base price: ${args.base_price}")
    print(f"Seed: {args.seed}")

    try:
        # Create environment with demand model integration disabled for training
        env: gym.Env = PricingEnv(
            base_price=args.base_price, 
            seed=args.seed,
            use_demand_model=False  # Disable for faster training
        )
        print("✅ Environment created successfully")
        
        # Create PPO model
        model: PPO = PPO(
            "MlpPolicy", 
            env, 
            verbose=1, 
            seed=args.seed,
            learning_rate=0.0003,
            n_steps=2048,
            batch_size=64,
            n_epochs=10
        )
        print("✅ PPO model initialized")
        
        # Train the model
        print(f"🏋️ Training for {args.steps} timesteps...")
        model.learn(total_timesteps=args.steps)
        print("✅ Training completed")

        # Save the model
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        model.save(MODEL_PATH.as_posix())
        print(f"✅ Model saved to {MODEL_PATH.relative_to(Path('.').absolute())}")
        
        # Test the trained model
        print("\n🧪 Testing trained model...")
        obs, _ = env.reset()
        for i in range(5):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            multiplier = action[0]
            price = info['price']
            demand = info['demand']
            revenue = info['revenue']
            print(f"  Step {i+1}: Price=${price:.2f} (×{multiplier:.2f}), Demand={demand:.2f}, Revenue=${revenue:.2f}")
            if done or truncated:
                break
        
        print("\n🎯 Training completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
