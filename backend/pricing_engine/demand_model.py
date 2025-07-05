import os
import torch
import torch.nn as nn
import joblib
import numpy as np
from backend.database import get_sales_data, get_external_factors
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = './models'

class SimpleDemandNet(nn.Module):
    """Simple neural network for demand forecasting."""
    def __init__(self, input_size, hidden_size=64):
        super(SimpleDemandNet, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        demand = self.fc(last_output)
        return demand

class DemandModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and scaler."""
        try:
            model_path = os.path.join(CACHE_DIR, 'pytorch_model.bin')
            scaler_path = os.path.join(CACHE_DIR, 'scaler.pkl')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                # Load model checkpoint
                checkpoint = torch.load(model_path, map_location='cpu')
                
                # Initialize model with saved parameters
                self.model = SimpleDemandNet(
                    input_size=checkpoint['input_size'],
                    hidden_size=checkpoint['hidden_size']
                )
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.eval()
                
                # Load scaler
                self.scaler = joblib.load(scaler_path)
                
                logger.info("✅ Model and scaler loaded successfully")
            else:
                logger.warning("Model files not found. Train the model first.")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.scaler = None

    async def fetch_data(self, start_date:str, end_date:str) -> Tuple:
        """Fetch and prepare data for prediction."""
        # Fetch sales and factors data
        sales_data = await get_sales_data(start_date, end_date)
        factors_data = await get_external_factors(start_date, end_date)
        # Here you should implement merging and processing like normalization, encoding
        return sales_data, factors_data

    def predict(self, sequences, device: str | torch.device = "cpu") -> Optional[np.ndarray]:
        """Forecast demand using time-series data."""
        try:
            if self.model is None or self.scaler is None:
                logger.error("Model not loaded. Cannot make predictions.")
                return None
            
            # Ensure sequences is a numpy array with correct shape
            if isinstance(sequences, list):
                sequences = np.array(sequences)
            
            # If single sequence, add batch dimension
            if sequences.ndim == 2:
                sequences = sequences[np.newaxis, :]
            
            # Normalize the input sequences
            batch_size, seq_len, n_features = sequences.shape
            sequences_reshaped = sequences.reshape(-1, n_features)
            sequences_scaled = self.scaler.transform(sequences_reshaped)
            sequences_scaled = sequences_scaled.reshape(batch_size, seq_len, n_features)
            
            # Convert to tensor and make prediction
            inputs = torch.FloatTensor(sequences_scaled).to(device)
            self.model.to(device)
            self.model.eval()
            
            with torch.no_grad():
                outputs = self.model(inputs)
                predictions = outputs.cpu().numpy()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return None
