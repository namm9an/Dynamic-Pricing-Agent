from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import asyncio
from pathlib import Path
import logging
import time
from datetime import datetime
import json
from typing import Optional
import uuid

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
from backend.cache import cache_manager
from backend.auth import auth_manager, get_current_user, RequireScopes, User, Token, oauth

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pricing_agent.log') if os.getenv('LOG_TO_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger('pricing_agent')

# Global metrics storage (in production, use Redis or database)
metrics_store = {
    'requests': 0,
    'errors': 0,
    'response_times': [],
    'revenue_decisions': [],
    'feedback_data': []
}

app = FastAPI(
    title="Dynamic Pricing Agent API",
    version="3.0.0",
    description="Production-ready dynamic pricing system with monitoring and feedback loops"
)

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

# Middleware for request tracking
@app.middleware("http")
async def track_requests(request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Log request
    logger.info(f"Request {request_id}: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Track metrics
        metrics_store['requests'] += 1
        metrics_store['response_times'].append(process_time)
        
        # Keep only last 1000 response times for memory efficiency
        if len(metrics_store['response_times']) > 1000:
            metrics_store['response_times'] = metrics_store['response_times'][-1000:]
            
        logger.info(f"Request {request_id} completed in {process_time:.3f}s")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        metrics_store['errors'] += 1
        logger.error(f"Request {request_id} failed: {str(e)}")
        raise

# CORS configuration for production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://dynamic-pricing.vercel.app",  # Production frontend
    os.getenv("FRONTEND_URL", "*")  # Environment-specific frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class DemandQuery(BaseModel):
    price: float
    location: str
    product_id: str = "PROD_001"
    days: int = 30

class FeedbackData(BaseModel):
    price_set: float
    actual_demand: float
    revenue_generated: float
    product_id: str = "PROD_001"
    location: str = "US"
    timestamp: Optional[datetime] = None
    ab_test_group: Optional[str] = None

class SystemMetrics(BaseModel):
    total_requests: int
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    uptime_hours: float
    model_version: str

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
    """Enhanced health-check endpoint with system metrics."""
    response_times = metrics_store['response_times']
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "metrics": {
            "total_requests": metrics_store['requests'],
            "total_errors": metrics_store['errors'],
            "error_rate": metrics_store['errors'] / max(metrics_store['requests'], 1) * 100,
            "avg_response_time": np.mean(response_times) if response_times else 0,
            "p95_response_time": np.percentile(response_times, 95) if len(response_times) >= 20 else 0,
            "model_status": "loaded" if demand_model else "fallback",
            "torch_available": TORCH_AVAILABLE,
            "cache_status": cache_manager.health_check()
        }
    }

@app.post('/predict-demand')
async def predict_demand(query: DemandQuery):
    """Predict demand for given price, location, and product."""
    logger.info(f"Demand prediction request for {query.product_id} at price {query.price} in {query.location}")
    
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
    logger.info(f"Optimal price request for {req.product_id} with base price {req.base_price} in {req.location}")
    
    # Create cache key
    cache_key = f"price:{req.product_id}:{req.location}:{req.base_price}"
    
    # Check cache first
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for {cache_key}")
        return cached_result
    
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
        
        # Track revenue decision
        metrics_store['revenue_decisions'].append({
            "timestamp": datetime.utcnow().isoformat(),
            "product_id": req.product_id,
            "base_price": req.base_price,
            "optimal_price": res["optimal_price"],
            "expected_revenue": res["expected_revenue"],
            "demand_forecast": demand_val
        })
        
        logger.info(f"Price recommendation: ${res['optimal_price']:.2f} (expected revenue: ${res['expected_revenue']:.2f})")
        
        result = {
            "optimal_price": res["optimal_price"],
            "expected_revenue": res["expected_revenue"],
            "demand_forecast": demand_val,
        }
        
        # Cache the result
        cache_manager.set(cache_key, result, ttl=300)  # Cache for 5 minutes
        
        return result
    except Exception as e:
        logger.error(f"Optimal price error for {req.product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimal price error: {str(e)}")

# New endpoints for Phase 3

@app.post("/record-outcome")
async def record_outcome(feedback: FeedbackData, background_tasks: BackgroundTasks):
    """Record actual outcomes for retraining feedback loop."""
    try:
        if feedback.timestamp is None:
            feedback.timestamp = datetime.utcnow()
            
        feedback_record = {
            "timestamp": feedback.timestamp.isoformat() if feedback.timestamp else datetime.utcnow().isoformat(),
            "product_id": feedback.product_id,
            "location": feedback.location,
            "price_set": feedback.price_set,
            "actual_demand": feedback.actual_demand,
            "revenue_generated": feedback.revenue_generated,
            "ab_test_group": feedback.ab_test_group
        }
        
        # Store feedback (in production, save to database)
        metrics_store['feedback_data'].append(feedback_record)
        
        # Keep only last 10000 feedback records for memory efficiency
        if len(metrics_store['feedback_data']) > 10000:
            metrics_store['feedback_data'] = metrics_store['feedback_data'][-10000:]
            
        logger.info(f"Recorded outcome: {feedback.product_id} - Price: ${feedback.price_set}, Demand: {feedback.actual_demand}, Revenue: ${feedback.revenue_generated}")
        
        # Schedule background task for potential model update
        background_tasks.add_task(check_retraining_trigger)
        
        return {
            "status": "recorded",
            "timestamp": feedback_record["timestamp"],
            "feedback_id": len(metrics_store['feedback_data'])
        }
        
    except Exception as e:
        logger.error(f"Failed to record outcome: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record outcome: {str(e)}")

@app.get("/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics for monitoring dashboard."""
    try:
        response_times = metrics_store['response_times']
        
        # Calculate performance metrics
        avg_response_time = np.mean(response_times) if response_times else 0
        p95_response_time = np.percentile(response_times, 95) if len(response_times) >= 20 else 0
        error_rate = metrics_store['errors'] / max(metrics_store['requests'], 1) * 100
        
        # Recent feedback analysis
        recent_feedback = metrics_store['feedback_data'][-100:] if metrics_store['feedback_data'] else []
        avg_revenue = np.mean([f['revenue_generated'] for f in recent_feedback]) if recent_feedback else 0
        
        # Revenue decisions analysis
        recent_decisions = metrics_store['revenue_decisions'][-100:] if metrics_store['revenue_decisions'] else []
        avg_price_change = 0
        if len(recent_decisions) > 1:
            price_changes = [abs(d['optimal_price'] - d['base_price']) / d['base_price'] 
                           for d in recent_decisions if d['base_price'] > 0]
            avg_price_change = np.mean(price_changes) * 100 if price_changes else 0
        
        return {
            "system_health": {
                "status": "healthy" if error_rate < 5 else "degraded",
                "uptime_hours": (time.time() - app.state.start_time) / 3600 if hasattr(app.state, 'start_time') else 0,
                "total_requests": metrics_store['requests'],
                "error_rate": round(error_rate, 2),
                "avg_response_time": round(avg_response_time * 1000, 2),  # Convert to ms
                "p95_response_time": round(p95_response_time * 1000, 2)   # Convert to ms
            },
            "model_performance": {
                "model_status": "loaded" if demand_model else "fallback",
                "torch_available": TORCH_AVAILABLE,
                "total_predictions": len(recent_decisions),
                "avg_revenue_per_decision": round(avg_revenue, 2),
                "avg_price_change_percent": round(avg_price_change, 2)
            },
            "feedback_loop": {
                "total_feedback_records": len(metrics_store['feedback_data']),
                "recent_feedback_count": len(recent_feedback),
                "last_feedback_time": recent_feedback[-1]['timestamp'] if recent_feedback else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/ab-test/{user_id}")
async def get_ab_test_group(user_id: str):
    """Assign user to A/B test group for pricing experiments."""
    try:
        # Simple hash-based assignment for consistent grouping
        hash_value = hash(user_id) % 100
        
        # 50/50 split between control and test groups
        group = "test" if hash_value < 50 else "control"
        
        logger.info(f"User {user_id} assigned to A/B test group: {group}")
        
        return {
            "user_id": user_id,
            "ab_test_group": group,
            "strategy": "dynamic_pricing" if group == "test" else "static_pricing",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to assign A/B test group: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign A/B test group: {str(e)}")

async def check_retraining_trigger():
    """Background task to check if model retraining should be triggered."""
    try:
        feedback_count = len(metrics_store['feedback_data'])
        
        # Trigger retraining if we have enough new feedback data
        if feedback_count > 0 and feedback_count % 100 == 0:
            logger.info(f"Retraining trigger: {feedback_count} feedback records collected")
            # In production, this would trigger a background job or webhook
            # For now, just log the trigger event
            
    except Exception as e:
        logger.error(f"Error in retraining trigger check: {str(e)}")

# OAuth2 authentication endpoints

@app.get("/auth/login/{provider}")
async def login(provider: str, request: Request):
    """Initiate OAuth login flow"""
    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@app.get("/auth/callback/{provider}")
async def auth_callback(provider: str, request: Request):
    """Handle OAuth callback and issue tokens"""
    user_data = await auth_manager.handle_oauth_callback(provider, request)
    tokens = auth_manager.create_user_tokens(user_data)
    return tokens

@app.post('/auth/token_refresh')
async def refresh_access_token(request: Request):
    """Refresh access token using refresh token"""
    refresh_token = request.json().get('refresh_token')
    
    try:
        token_data = auth_manager.verify_token(refresh_token, "refresh")
        user_id = token_data.username
        
        # Create new access token
        new_access_token = auth_manager.create_access_token({
            "sub": user_id,
            "scopes": token_data.scopes
        })
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh access token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token refresh error: {str(e)}")

# Initialize app start time for uptime calculation
@app.on_event("startup")
async def set_start_time():
    app.state.start_time = time.time()
