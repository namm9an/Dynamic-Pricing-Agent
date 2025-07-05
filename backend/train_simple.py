"""Simplified PPO training script for pricing agent.

This version uses a lightweight implementation without torch dependencies.
"""
import json
import numpy as np
from pathlib import Path
import pickle
from typing import Dict, Tuple, List

# Create models directory
MODEL_DIR = Path("models/pricing_agent")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class SimplePPOAgent:
    """Simplified PPO agent for pricing decisions."""
    
    def __init__(self, learning_rate: float = 0.001, clip_ratio: float = 0.2):
        self.learning_rate = learning_rate
        self.clip_ratio = clip_ratio
        
        # Simple neural network weights (2 input -> 10 hidden -> 1 output)
        self.w1 = np.random.randn(2, 10) * 0.1
        self.b1 = np.zeros(10)
        self.w2 = np.random.randn(10, 1) * 0.1
        self.b2 = np.zeros(1)
        
        # Value function weights
        self.v_w1 = np.random.randn(2, 10) * 0.1
        self.v_b1 = np.zeros(10)
        self.v_w2 = np.random.randn(10, 1) * 0.1
        self.v_b2 = np.zeros(1)
        
        # Adam optimizer state
        self.m_w1, self.v_w1_opt = np.zeros_like(self.w1), np.zeros_like(self.w1)
        self.m_b1, self.v_b1_opt = np.zeros_like(self.b1), np.zeros_like(self.b1)
        self.m_w2, self.v_w2_opt = np.zeros_like(self.w2), np.zeros_like(self.w2)
        self.m_b2, self.v_b2_opt = np.zeros_like(self.b2), np.zeros_like(self.b2)
        
        self.t = 0  # timestep for Adam
        
    def _relu(self, x):
        return np.maximum(0, x)
    
    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def predict(self, obs: np.ndarray, deterministic: bool = False) -> Tuple[np.ndarray, None]:
        """Predict action (price multiplier) given observation."""
        # Forward pass through policy network
        h1 = self._relu(obs @ self.w1 + self.b1)
        logit = h1 @ self.w2 + self.b2
        
        # Convert to action in range [0.8, 1.5]
        action_raw = self._sigmoid(logit)
        action = 0.8 + action_raw * 0.7  # Maps [0,1] to [0.8, 1.5]
        
        if not deterministic:
            # Add small noise for exploration
            noise = np.random.normal(0, 0.05, size=action.shape)
            action = np.clip(action + noise, 0.8, 1.5)
        
        return action.reshape(1, -1), None
    
    def value(self, obs: np.ndarray) -> float:
        """Estimate value of state."""
        h1 = self._relu(obs @ self.v_w1 + self.v_b1)
        value = h1 @ self.v_w2 + self.v_b2
        return float(value[0])
    
    def update(self, obs: np.ndarray, action: float, reward: float, next_obs: np.ndarray, done: bool):
        """Simple gradient update (simplified PPO)."""
        self.t += 1
        
        # Compute advantage
        value = self.value(obs)
        next_value = self.value(next_obs) if not done else 0
        td_error = reward + 0.99 * next_value - value
        
        # Policy gradient (simplified)
        h1 = self._relu(obs @ self.w1 + self.b1)
        logit = h1 @ self.w2 + self.b2
        action_prob = self._sigmoid(logit)
        
        # Gradient of log probability
        grad_logit = (action - 0.8) / 0.7 - action_prob
        grad_w2 = h1.reshape(-1, 1) @ grad_logit.reshape(1, -1) * td_error
        grad_b2 = grad_logit * td_error
        
        # Backprop to first layer
        grad_h1 = grad_logit @ self.w2.T * td_error
        grad_h1[h1 <= 0] = 0  # ReLU gradient
        grad_w1 = obs.reshape(-1, 1) @ grad_h1.reshape(1, -1)
        grad_b1 = grad_h1.flatten()
        
        # Adam optimizer update
        beta1, beta2 = 0.9, 0.999
        eps = 1e-8
        
        # Update policy weights
        self._adam_update(self.w1, grad_w1, self.m_w1, self.v_w1_opt, beta1, beta2, eps)
        self._adam_update(self.b1, grad_b1, self.m_b1, self.v_b1_opt, beta1, beta2, eps)
        self._adam_update(self.w2, grad_w2, self.m_w2, self.v_w2_opt, beta1, beta2, eps)
        self._adam_update(self.b2, grad_b2.flatten(), self.m_b2, self.v_b2_opt, beta1, beta2, eps)
        
        # Update value function (simplified)
        value_loss_grad = -2 * td_error
        v_h1 = self._relu(obs @ self.v_w1 + self.v_b1)
        self.v_w2 -= self.learning_rate * v_h1.reshape(-1, 1) * value_loss_grad
        self.v_b2 -= self.learning_rate * value_loss_grad
        
    def _adam_update(self, param, grad, m, v, beta1, beta2, eps):
        """Adam optimizer update."""
        m[:] = beta1 * m + (1 - beta1) * grad
        v[:] = beta2 * v + (1 - beta2) * grad**2
        
        m_hat = m / (1 - beta1**(self.t))
        v_hat = v / (1 - beta2**(self.t))
        
        param[:] += self.learning_rate * m_hat / (np.sqrt(v_hat) + eps)
    
    def save(self, path: Path):
        """Save model weights."""
        weights = {
            'w1': self.w1, 'b1': self.b1,
            'w2': self.w2, 'b2': self.b2,
            'v_w1': self.v_w1, 'v_b1': self.v_b1,
            'v_w2': self.v_w2, 'v_b2': self.v_b2,
        }
        with open(path, 'wb') as f:
            pickle.dump(weights, f)
    
    def load(self, path: Path):
        """Load model weights."""
        with open(path, 'rb') as f:
            weights = pickle.load(f)
        self.w1 = weights['w1']
        self.b1 = weights['b1']
        self.w2 = weights['w2']
        self.b2 = weights['b2']
        self.v_w1 = weights['v_w1']
        self.v_b1 = weights['v_b1']
        self.v_w2 = weights['v_w2']
        self.v_b2 = weights['v_b2']


class SimplePricingEnv:
    """Simplified pricing environment."""
    
    def __init__(self, base_price: float = 10.0, max_steps: int = 50):
        self.base_price = base_price
        self.max_steps = max_steps
        self.step_count = 0
        self.last_multiplier = 1.0
        self.demand_forecast = 1.0
        
    def reset(self) -> Tuple[np.ndarray, Dict]:
        self.step_count = 0
        self.last_multiplier = 1.0
        self.demand_forecast = self._simulate_demand(1.0)
        return np.array([self.demand_forecast, self.last_multiplier]), {}
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        self.step_count += 1
        multiplier = float(np.clip(action[0], 0.8, 1.5))
        price = self.base_price * multiplier
        
        # Simulate demand
        demand = self._simulate_demand(multiplier)
        revenue = price * demand
        
        # Reward = revenue - price change penalty
        price_change_penalty = abs(multiplier - self.last_multiplier) * 0.1
        reward = revenue - price_change_penalty
        
        # Update state
        self.last_multiplier = multiplier
        self.demand_forecast = demand
        obs = np.array([self.demand_forecast, self.last_multiplier])
        
        done = self.step_count >= self.max_steps
        info = {
            'price': price,
            'demand': demand,
            'revenue': revenue,
            'penalty': price_change_penalty
        }
        
        return obs, reward, done, False, info
    
    def _simulate_demand(self, multiplier: float) -> float:
        """Simple demand simulation."""
        price = self.base_price * multiplier
        baseline = max(0.1, 2.0 - price * 0.05)
        noise = np.random.normal(0, 0.05)
        return float(max(0.0, baseline + noise))


def train_agent(steps: int = 10000, base_price: float = 10.0):
    """Train the simplified PPO agent."""
    env = SimplePricingEnv(base_price=base_price)
    agent = SimplePPOAgent()
    
    obs, _ = env.reset()
    episode_rewards = []
    current_episode_reward = 0
    
    print(f"Training SimplePPO agent for {steps} steps...")
    
    for step in range(steps):
        # Get action
        action, _ = agent.predict(obs, deterministic=False)
        
        # Take step
        next_obs, reward, done, _, info = env.step(action)
        current_episode_reward += reward
        
        # Update agent
        agent.update(obs, action[0], reward, next_obs, done)
        
        if done:
            episode_rewards.append(current_episode_reward)
            if len(episode_rewards) % 10 == 0:
                avg_reward = np.mean(episode_rewards[-10:])
                print(f"Step {step}, Episodes: {len(episode_rewards)}, Avg Reward: {avg_reward:.2f}")
            
            obs, _ = env.reset()
            current_episode_reward = 0
        else:
            obs = next_obs
        
        # Progress indicator
        if step % 1000 == 0 and step > 0:
            print(f"Progress: {step}/{steps} steps completed")
    
    # Save the model
    model_path = MODEL_DIR / "ppo_pricing.pkl"
    agent.save(model_path)
    print(f"\n✅ Model saved to {model_path}")
    
    # Also save a compatibility file for the main system
    compat_path = MODEL_DIR / "ppo_pricing.zip"
    with open(compat_path, 'wb') as f:
        pickle.dump({'agent': agent, 'type': 'SimplePPO'}, f)
    print(f"✅ Compatibility file saved to {compat_path}")
    
    # Save training stats
    stats = {
        'total_steps': steps,
        'total_episodes': len(episode_rewards),
        'final_avg_reward': np.mean(episode_rewards[-10:]) if episode_rewards else 0,
        'all_rewards': episode_rewards
    }
    
    stats_path = MODEL_DIR / "training_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Training stats saved to {stats_path}")
    
    return agent, stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train simplified PPO pricing agent")
    parser.add_argument("--steps", type=int, default=10000, help="Training steps")
    parser.add_argument("--base-price", type=float, default=10.0, help="Base product price")
    args = parser.parse_args()
    
    agent, stats = train_agent(steps=args.steps, base_price=args.base_price)
    
    print(f"\n🎯 Training complete!")
    print(f"Final average reward: {stats['final_avg_reward']:.2f}")
    print(f"Total episodes: {stats['total_episodes']}")
