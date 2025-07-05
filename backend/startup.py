"""
Startup module to handle automatic initialization tasks.
"""
import asyncio
from backend.database import get_client, get_sales_data, insert_sales_data, insert_external_factors
from backend.synthetic_data import generate_fake_demand_data
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_and_insert_fake_data():
    """Generate synthetic data and insert into Supabase if tables are empty."""
    try:
        logger.info("Checking if synthetic data generation is needed...")
        
        # Check if sales data exists
        sales_data = await get_sales_data()
        
        if len(sales_data) == 0:
            logger.info("No sales data found. Generating synthetic data...")
            
            # Generate synthetic data
            sales_df, external_df = generate_fake_demand_data(
                start_date="2023-01-01",
                end_date="2024-12-31",
                num_products=10,
                num_locations=5
            )
            
            logger.info(f"Generated {len(sales_df)} sales records and {len(external_df)} external factor records")
            
            # Convert DataFrames to list of dicts for insertion
            sales_records = sales_df.to_dict('records')
            external_records = external_df.to_dict('records')
            
            # Insert data in batches to avoid timeout
            batch_size = 100
            
            # Insert sales data
            for i in range(0, len(sales_records), batch_size):
                batch = sales_records[i:i+batch_size]
                for record in batch:
                    await insert_sales_data(record)
                logger.info(f"Inserted sales batch {i//batch_size + 1}/{(len(sales_records) + batch_size - 1)//batch_size}")
            
            # Insert external factors
            for i in range(0, len(external_records), batch_size):
                batch = external_records[i:i+batch_size]
                for record in batch:
                    await insert_external_factors(record)
                logger.info(f"Inserted external factors batch {i//batch_size + 1}/{(len(external_records) + batch_size - 1)//batch_size}")
            
            logger.info("✅ Synthetic data generation and insertion completed!")
            return True
        else:
            logger.info(f"Found {len(sales_data)} existing sales records. Skipping synthetic data generation.")
            return False
            
    except Exception as e:
        logger.error(f"Error in synthetic data generation: {e}")
        return False

async def check_and_train_model():
    """Check if model exists, train if needed."""
    import os
    from pathlib import Path
    
    model_path = Path("./models/pytorch_model.bin")
    
    if not model_path.exists():
        logger.info("Trained model not found. Training model...")
        
        # Import here to avoid circular imports
        from backend.train_demand import train_model
        
        try:
            train_model()
            logger.info("✅ Model training completed!")
        except Exception as e:
            logger.error(f"Error training model: {e}")
            logger.info("Will use fallback demand calculation")
    else:
        logger.info("✅ Trained model found at ./models/pytorch_model.bin")

async def initialize_system():
    """Run all startup tasks."""
    logger.info("🚀 Initializing Dynamic Pricing Agent...")
    
    # 1. Check and generate synthetic data if needed
    await generate_and_insert_fake_data()
    
    # 2. Check and train model if needed
    await check_and_train_model()
    
    logger.info("✅ System initialization complete!")

if __name__ == "__main__":
    asyncio.run(initialize_system())
