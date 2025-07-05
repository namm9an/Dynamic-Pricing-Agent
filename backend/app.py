from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import asyncio
from pathlib import Path

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None

from pydantic import BaseModel
from fastapi import HTTPException

try:
    from backend.pricing_engine.demand_model import DemandModel
except (ImportError, OSError):
    DemandModel = None
    
from backend.pricing_engine.rl_agent import recommend_price
from backend.synthetic_data import generate_sample_data_for_product
from backend.startup import initialize_system

load_dotenv()

app = FastAPI(title="Dynamic Pricing Agent API")

# Global variable for the demand model
demand_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    await initialize_system()
    
    # Initialize the demand model
    global demand_model
    try:
        demand_model = DemandModel()
        print("✅ Demand model loaded successfully")
    except Exception as e:
        print(f"⚠️ Could not load demand model: {e}")
        print("Will use fallback demand calculation")

# Allow local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DemandQuery(BaseModel):
    price: float
    location: str
    product_id: str = "PROD_001"
    days: int = 30

def generate_input_sequence(price: float, location: str, product_id: str, days: int = 30):
    """Generate input sequence for demand prediction."""
    # For now, use synthetic data as fallback
    sample_data = generate_sample_data_for_product(product_id, location, days)
    
    # Create features array
    features = ['price', 'units_sold', 'is_holiday', 'weather_code']
    sequence = sample_data[features].values
    
    # Use last 7 days as input and modify the price for prediction
    if len(sequence) >= 7:
        input_sequence = sequence[-7:].copy()
        # Modify the last entry's price to the queried price
        input_sequence[-1, 0] = price  # price is the first feature
        return input_sequence.tolist()
    else:
        # If not enough data, create a simple sequence
        return [[price, 50, False, 1] for _ in range(7)]

@app.get("/health")
async def health_check():
    """Simple health-check endpoint used by CI/CD and container orchestrators."""
    return {"status": "active"}

@app.post('/predict-demand')
async def predict_demand(query: DemandQuery):
    """Predict demand for given price, location, and product."""
    try:
        # Generate input sequence using synthetic data as fallback
        sequences = generate_input_sequence(
            query.price, 
            query.location, 
            query.product_id, 
            query.days
        )
        
        # Try to use trained model first
        if (demand_model is not None and TORCH_AVAILABLE and 
            Path("./models/pytorch_model.bin").exists()):
            try:
                # Convert sequences to tensor
                input_tensor = torch.tensor([sequences], dtype=torch.float32)
                
                # Get prediction from model
                with torch.no_grad():
                    prediction = demand_model.predict(input_tensor)
                    
                # Extract predicted demand value
                if prediction is not None:
                    predicted_demand = float(prediction[0])
                    model_version = '1.0-transformer'
                else:
                    raise ValueError("Model returned None")
                    
            except Exception as e:
                print(f"Model prediction failed: {e}")
                # Fall back to simple model
                base_demand = 100
                price_elasticity = -0.8
                predicted_demand = max(1, base_demand + (50 - query.price) * price_elasticity)
                model_version = '1.0-fallback'
        else:
            # Use simple demand model as fallback
            base_demand = 100
            price_elasticity = -0.8
            predicted_demand = max(1, base_demand + (50 - query.price) * price_elasticity)
            model_version = '1.0-fallback'
        
        return {
            'predicted_demand': round(predicted_demand, 2),
            'price': query.price,
            'location': query.location,
            'product_id': query.product_id,
            'model_version': model_version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


class OptimalPriceRequest(BaseModel):
    base_price: float
    product_id: str = "PROD_001"
    location: str = "US"
    context: dict[str, str | int | float] | None = None  # reserved for future use


@app.post("/get-optimal-price")
async def get_optimal_price(req: OptimalPriceRequest):
    """Return price suggested by RL agent along with expected revenue."""
    try:
        # Re-use demand estimation endpoint logic
        demand_resp = await predict_demand(
            DemandQuery(
                price=req.base_price,
                location=req.location,
                product_id=req.product_id,
                days=30,
            )
        )
        demand_val = demand_resp["predicted_demand"]
        res = recommend_price(demand_val, last_multiplier=1.0, base_price=req.base_price)
        return {
            "optimal_price": res["optimal_price"],
            "expected_revenue": res["expected_revenue"],
            "demand_forecast": demand_val,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimal price error: {str(e)}")
