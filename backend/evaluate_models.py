"""Evaluation script to compare RL pricing agent with baseline strategies.

This script:
1. Tests the RL agent against static and rule-based pricing
2. Measures revenue lift and price stability
3. Generates performance metrics for dashboard
"""
from __future__ import annotations

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Add D:\PythonPackages to sys.path for dependencies
if "D:\\PythonPackages" not in sys.path:
    sys.path.insert(0, "D:\\PythonPackages")

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = "D:\\PythonPackages" + os.pathsep + os.environ.get('PYTHONPATH', '')

# Add backend to path
sys.path.append(str(Path(__file__).parent))

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from pricing_engine.rl_env import PricingEnv
from pricing_engine.rl_agent import load, MODEL_PATH
from pricing_engine.simulator import simulate_period


def evaluate_static_pricing(
    env: PricingEnv, 
    price: float, 
    episodes: int = 10, 
    steps_per_episode: int = 50
) -> Dict[str, float]:
    """Evaluate static pricing strategy."""
    total_revenue = 0
    revenues = []
    
    for _ in range(episodes):
        obs, _ = env.reset()
        episode_revenue = 0
        
        for _ in range(steps_per_episode):
            # Static strategy: always use the same price
            multiplier = price / env.base_price
            action = np.array([multiplier], dtype=np.float32)
            
            obs, reward, done, truncated, info = env.step(action)
            episode_revenue += info["revenue"]
            
            if done or truncated:
                break
                
        revenues.append(episode_revenue)
        total_revenue += episode_revenue
    
    return {
        "strategy": "static",
        "price": price,
        "avg_revenue": total_revenue / episodes,
        "std_revenue": np.std(revenues),
        "min_revenue": min(revenues),
        "max_revenue": max(revenues)
    }


def evaluate_rule_based_pricing(
    env: PricingEnv, 
    episodes: int = 10, 
    steps_per_episode: int = 50
) -> Dict[str, float]:
    """Evaluate rule-based pricing strategy (simple demand-responsive)."""
    total_revenue = 0
    revenues = []
    
    for _ in range(episodes):
        obs, _ = env.reset()
        episode_revenue = 0
        
        for _ in range(steps_per_episode):
            # Rule-based: higher price when demand is low, lower when high
            demand_forecast = obs[0]
            if demand_forecast > 1.5:
                multiplier = 0.9  # Lower price for high demand
            elif demand_forecast < 0.5:
                multiplier = 1.3  # Higher price for low demand
            else:
                multiplier = 1.0  # Base price for normal demand
                
            action = np.array([multiplier], dtype=np.float32)
            obs, reward, done, truncated, info = env.step(action)
            episode_revenue += info["revenue"]
            
            if done or truncated:
                break
                
        revenues.append(episode_revenue)
        total_revenue += episode_revenue
    
    return {
        "strategy": "rule_based",
        "avg_revenue": total_revenue / episodes,
        "std_revenue": np.std(revenues),
        "min_revenue": min(revenues),
        "max_revenue": max(revenues)
    }


def evaluate_rl_agent(
    env: PricingEnv, 
    episodes: int = 10, 
    steps_per_episode: int = 50
) -> Tuple[Dict[str, float], List[float]]:
    """Evaluate trained RL agent."""
    try:
        model = load()
        print("✅ RL agent loaded successfully")
    except FileNotFoundError:
        print("⚠️ No trained RL model found. Please train the agent first.")
        return None, []
    
    total_revenue = 0
    revenues = []
    price_changes = []
    
    for _ in range(episodes):
        obs, _ = env.reset()
        episode_revenue = 0
        last_price = env.base_price
        
        for _ in range(steps_per_episode):
            # Handle different model types (SB3 vs simplified)
            if hasattr(model, 'predict'):
                action, _ = model.predict(obs, deterministic=True)
                if len(action.shape) > 0 and action.shape[0] == 1:
                    action = action[0]  # Handle SB3 format
            else:
                # Fallback heuristic
                demand_forecast = obs[0]
                if demand_forecast > 1.5:
                    action = np.array([0.9])
                elif demand_forecast < 0.5:
                    action = np.array([1.3])
                else:
                    action = np.array([1.0])
            
            obs, reward, done, truncated, info = env.step(action)
            
            episode_revenue += info["revenue"]
            current_price = info["price"]
            price_changes.append(abs(current_price - last_price) / last_price)
            last_price = current_price
            
            if done or truncated:
                break
                
        revenues.append(episode_revenue)
        total_revenue += episode_revenue
    
    return {
        "strategy": "rl_agent",
        "avg_revenue": total_revenue / episodes,
        "std_revenue": np.std(revenues),
        "min_revenue": min(revenues),
        "max_revenue": max(revenues),
        "avg_price_change": np.mean(price_changes),
        "max_price_change": max(price_changes)
    }, price_changes


def generate_comparison_plot(results: List[Dict], output_path: str = "pricing_comparison.png"):
    """Generate bar chart comparing strategies."""
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️ Matplotlib not available, skipping plot generation")
        return
        
    strategies = [r["strategy"] for r in results]
    revenues = [r["avg_revenue"] for r in results]
    stds = [r["std_revenue"] for r in results]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(strategies, revenues, yerr=stds, capsize=10)
    
    # Color code bars
    colors = ['#ff7f0e', '#2ca02c', '#1f77b4']  # Orange, Green, Blue
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    plt.xlabel('Pricing Strategy')
    plt.ylabel('Average Revenue')
    plt.title('Pricing Strategy Performance Comparison')
    
    # Add value labels on bars
    for bar, revenue in zip(bars, revenues):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${revenue:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"✅ Comparison plot saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate pricing strategies")
    parser.add_argument("--episodes", type=int, default=10, help="Number of evaluation episodes")
    parser.add_argument("--steps", type=int, default=50, help="Steps per episode")
    parser.add_argument("--base-price", type=float, default=10.0, help="Base product price")
    parser.add_argument("--plot", action="store_true", help="Generate comparison plot")
    args = parser.parse_args()
    
    print(f"🔍 Evaluating pricing strategies...")
    print(f"Episodes: {args.episodes}, Steps per episode: {args.steps}")
    print(f"Base price: ${args.base_price}")
    
    # Create environment (disable demand model for faster evaluation)
    env = PricingEnv(base_price=args.base_price, max_steps=args.steps, use_demand_model=False)
    
    results = []
    
    # Evaluate static pricing at base price
    print("\n📊 Evaluating static pricing...")
    static_result = evaluate_static_pricing(env, args.base_price, args.episodes, args.steps)
    results.append(static_result)
    print(f"Static pricing: ${static_result['avg_revenue']:.2f} ± ${static_result['std_revenue']:.2f}")
    
    # Evaluate rule-based pricing
    print("\n📊 Evaluating rule-based pricing...")
    rule_result = evaluate_rule_based_pricing(env, args.episodes, args.steps)
    results.append(rule_result)
    print(f"Rule-based pricing: ${rule_result['avg_revenue']:.2f} ± ${rule_result['std_revenue']:.2f}")
    
    # Evaluate RL agent
    print("\n📊 Evaluating RL agent...")
    rl_result, price_changes = evaluate_rl_agent(env, args.episodes, args.steps)
    if rl_result:
        results.append(rl_result)
        print(f"RL agent: ${rl_result['avg_revenue']:.2f} ± ${rl_result['std_revenue']:.2f}")
        print(f"Average price change: {rl_result['avg_price_change']*100:.1f}%")
        
        # Calculate revenue lift
        baseline_revenue = static_result['avg_revenue']
        rl_revenue = rl_result['avg_revenue']
        lift = (rl_revenue - baseline_revenue) / baseline_revenue * 100
        print(f"\n🎯 Revenue lift over static pricing: {lift:.1f}%")
        
        # Check if meets criteria
        if lift >= 5:
            print("✅ Meets minimum 5% revenue lift requirement!")
        else:
            print("⚠️ Below 5% revenue lift target")
            
        if rl_result['max_price_change'] < 0.15:
            print("✅ Price stability maintained (max change < 15%)")
        else:
            print("⚠️ Price changes exceed 15% threshold")
    
    # Save results
    results_path = Path("evaluation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📊 Results saved to {results_path}")
    
    # Generate plot if requested and possible
    if args.plot and len(results) >= 2:
        generate_comparison_plot(results)


if __name__ == "__main__":
    main()
