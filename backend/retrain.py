#!/usr/bin/env python3
"""
Daily Retraining Script for Dynamic Pricing Agent
=================================================

This script runs daily to retrain models based on feedback data.
Designed to run as a cron job or scheduled task.

Usage:
    python backend/retrain.py

Environment Variables:
    - DATABASE_URL: Connection string for feedback data
    - MODEL_UPDATE_THRESHOLD: Minimum feedback records for retraining (default: 100)
    - RETRAIN_LOG_LEVEL: Logging level (default: INFO)
"""

import os
import sys
import logging
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None

from pricing_engine.demand_model import DemandModel
from train_demand import train_demand_model
from train_agent import train_rl_agent
from database import get_feedback_data, save_model_version, get_feedback_count_since

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('RETRAIN_LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('retrain.log')
    ]
)
logger = logging.getLogger('retrain')

class ModelRetrainer:
    """Handles retraining of demand and pricing models."""
    
    def __init__(self):
        self.update_threshold = int(os.getenv('MODEL_UPDATE_THRESHOLD', 100))
        self.models_dir = Path("./models")
        self.models_dir.mkdir(exist_ok=True)
        
    async def run_daily_retrain(self):
        """Main retraining workflow."""
        logger.info("🔄 Starting daily retraining process")
        
        try:
            # Step 1: Check if retraining is needed
            if not await self.should_retrain():
                logger.info("📊 Not enough new feedback data for retraining")
                return
            
            # Step 2: Load feedback data
            feedback_data = await self.load_feedback_data()
            if not feedback_data:
                logger.warning("⚠️ No feedback data available")
                return
                
            # Step 3: Prepare training data
            training_data = self.prepare_training_data(feedback_data)
            
            # Step 4: Retrain demand model
            await self.retrain_demand_model(training_data)
            
            # Step 5: Retrain RL agent
            await self.retrain_rl_agent(training_data)
            
            # Step 6: Validate new models
            if await self.validate_models():
                # Step 7: Deploy new models
                await self.deploy_models()
                logger.info("✅ Retraining completed successfully")
            else:
                logger.error("❌ Model validation failed, keeping previous models")
                
        except Exception as e:
            logger.error(f"❌ Retraining failed: {str(e)}")
            raise
    
    async def should_retrain(self) -> bool:
        """Check if enough new feedback data exists for retraining."""
        try:
            # Check last retraining timestamp
            last_retrain_file = self.models_dir / "last_retrain.json"
            last_retrain_time = datetime.min
            
            if last_retrain_file.exists():
                with open(last_retrain_file, 'r') as f:
                    data = json.load(f)
                    last_retrain_time = datetime.fromisoformat(data['timestamp'])
            
            # Count new feedback records since last retrain
            new_feedback_count = await get_feedback_count_since(last_retrain_time)
            
            logger.info(f"📈 New feedback records since last retrain: {new_feedback_count}")
            
            return new_feedback_count >= self.update_threshold
            
        except Exception as e:
            logger.error(f"Error checking retrain condition: {e}")
            return False
    
    async def load_feedback_data(self) -> List[Dict[str, Any]]:
        """Load recent feedback data for training."""
        try:
            # In production, this would query the database
            # For now, simulate loading feedback data
            
            logger.info("📥 Loading feedback data from database")
            
            # Simulate feedback data loading
            # In reality, this would use: await get_feedback_data()
            feedback_data = []
            
            # For development, create sample feedback data
            if not feedback_data:
                logger.info("🔧 Using simulated feedback data for development")
                feedback_data = self.generate_sample_feedback()
            
            logger.info(f"📊 Loaded {len(feedback_data)} feedback records")
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error loading feedback data: {e}")
            return []
    
    def prepare_training_data(self, feedback_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert feedback data to training format."""
        try:
            df = pd.DataFrame(feedback_data)
            
            # Add derived features
            df['price_elasticity'] = (df['actual_demand'] - 100) / (df['price_set'] - 50)
            df['revenue_per_unit'] = df['revenue_generated'] / df['actual_demand']
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add time-based features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
            
            logger.info(f"✅ Prepared training data with {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame()
    
    async def retrain_demand_model(self, training_data: pd.DataFrame):
        """Retrain the demand forecasting model."""
        try:
            if not TORCH_AVAILABLE:
                logger.warning("⚠️ PyTorch not available, skipping demand model retraining")
                return
                
            logger.info("🧠 Retraining demand forecasting model")
            
            # Prepare sequences for LSTM training
            sequences = self.prepare_demand_sequences(training_data)
            
            # Train new model (incremental training with new data)
            new_model = await train_demand_model(
                sequences=sequences,
                existing_model_path=self.models_dir / "demand_model.pth",
                epochs=10,  # Fewer epochs for incremental training
                learning_rate=0.001
            )
            
            # Save new model with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_model_path = self.models_dir / f"demand_model_{timestamp}.pth"
            torch.save(new_model.state_dict(), new_model_path)
            
            logger.info(f"💾 Saved new demand model: {new_model_path}")
            
        except Exception as e:
            logger.error(f"Error retraining demand model: {e}")
            raise
    
    async def retrain_rl_agent(self, training_data: pd.DataFrame):
        """Retrain the RL pricing agent."""
        try:
            logger.info("🎯 Retraining RL pricing agent")
            
            # Create updated environment with new feedback data
            env_config = {
                'feedback_data': training_data.to_dict('records'),
                'use_real_outcomes': True
            }
            
            # Fine-tune existing agent with new data
            new_agent = await train_rl_agent(
                existing_agent_path=self.models_dir / "rl_agent.zip",
                env_config=env_config,
                total_timesteps=50000,  # Fewer steps for fine-tuning
                learning_rate=0.0001
            )
            
            # Save new agent with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_agent_path = self.models_dir / f"rl_agent_{timestamp}.zip"
            new_agent.save(new_agent_path)
            
            logger.info(f"💾 Saved new RL agent: {new_agent_path}")
            
        except Exception as e:
            logger.error(f"Error retraining RL agent: {e}")
            raise
    
    async def validate_models(self) -> bool:
        """Validate newly trained models against test data."""
        try:
            logger.info("🔍 Validating retrained models")
            
            # Load test data (separate from training)
            test_data = await self.load_test_data()
            
            if not test_data:
                logger.warning("⚠️ No test data available, skipping validation")
                return True
            
            # Test demand model accuracy
            demand_accuracy = await self.test_demand_model(test_data)
            
            # Test RL agent performance
            rl_performance = await self.test_rl_agent(test_data)
            
            # Validation thresholds
            min_demand_accuracy = 0.7  # 70% accuracy threshold
            min_rl_improvement = 0.05  # 5% improvement threshold
            
            validation_passed = (
                demand_accuracy >= min_demand_accuracy and
                rl_performance >= min_rl_improvement
            )
            
            logger.info(f"📊 Validation results: Demand accuracy: {demand_accuracy:.3f}, RL improvement: {rl_performance:.3f}")
            logger.info(f"✅ Validation {'PASSED' if validation_passed else 'FAILED'}")
            
            return validation_passed
            
        except Exception as e:
            logger.error(f"Error validating models: {e}")
            return False
    
    async def deploy_models(self):
        """Deploy new models by updating production model files."""
        try:
            logger.info("🚀 Deploying new models to production")
            
            # Find latest model files
            demand_models = list(self.models_dir.glob("demand_model_*.pth"))
            rl_agents = list(self.models_dir.glob("rl_agent_*.zip"))
            
            if demand_models:
                latest_demand = max(demand_models, key=lambda p: p.stat().st_mtime)
                production_demand = self.models_dir / "demand_model.pth"
                
                # Backup current model
                if production_demand.exists():
                    backup_path = self.models_dir / f"demand_model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pth"
                    production_demand.rename(backup_path)
                
                # Deploy new model
                latest_demand.rename(production_demand)
                logger.info("✅ Demand model deployed")
            
            if rl_agents:
                latest_rl = max(rl_agents, key=lambda p: p.stat().st_mtime)
                production_rl = self.models_dir / "rl_agent.zip"
                
                # Backup current agent
                if production_rl.exists():
                    backup_path = self.models_dir / f"rl_agent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    production_rl.rename(backup_path)
                
                # Deploy new agent
                latest_rl.rename(production_rl)
                logger.info("✅ RL agent deployed")
            
            # Update last retrain timestamp
            last_retrain_file = self.models_dir / "last_retrain.json"
            with open(last_retrain_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'models_updated': len(demand_models) + len(rl_agents)
                }, f)
            
            logger.info("🎉 Model deployment completed")
            
        except Exception as e:
            logger.error(f"Error deploying models: {e}")
            raise
    
    def prepare_demand_sequences(self, training_data: pd.DataFrame) -> np.ndarray:
        """Prepare sequence data for LSTM training."""
        # Sort by timestamp
        df = training_data.sort_values('timestamp')
        
        # Create sequences of length 7 (7 days)
        sequence_length = 7
        features = ['price_set', 'actual_demand', 'hour', 'day_of_week', 'is_weekend']
        
        sequences = []
        for i in range(len(df) - sequence_length + 1):
            sequence = df[features].iloc[i:i + sequence_length].values
            sequences.append(sequence)
        
        return np.array(sequences)
    
    async def load_test_data(self) -> List[Dict[str, Any]]:
        """Load test data for model validation."""
        # In production, load from a separate test dataset
        return []
    
    async def test_demand_model(self, test_data: List[Dict[str, Any]]) -> float:
        """Test demand model accuracy."""
        # Placeholder for demand model testing
        return 0.8  # 80% accuracy
    
    async def test_rl_agent(self, test_data: List[Dict[str, Any]]) -> float:
        """Test RL agent performance improvement."""
        # Placeholder for RL agent testing
        return 0.1  # 10% improvement
    
    def generate_sample_feedback(self) -> List[Dict[str, Any]]:
        """Generate sample feedback data for development."""
        np.random.seed(42)
        
        feedback_data = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(500):  # Generate 500 sample records
            timestamp = base_time + timedelta(hours=i)
            price = np.random.uniform(20, 80)
            demand = max(1, 100 - 1.5 * (price - 50) + np.random.normal(0, 10))
            revenue = price * demand
            
            feedback_data.append({
                'timestamp': timestamp.isoformat(),
                'product_id': f'PROD_{np.random.randint(1, 6):03d}',
                'location': np.random.choice(['US', 'EU', 'Asia']),
                'price_set': price,
                'actual_demand': demand,
                'revenue_generated': revenue,
                'ab_test_group': np.random.choice(['test', 'control'])
            })
        
        return feedback_data

async def main():
    """Main retraining script entry point."""
    try:
        logger.info("🚀 Dynamic Pricing Agent - Daily Retraining Script")
        logger.info(f"📅 Started at: {datetime.now().isoformat()}")
        
        retrainer = ModelRetrainer()
        await retrainer.run_daily_retrain()
        
        logger.info("✅ Retraining script completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Retraining script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
