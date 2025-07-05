import os
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from backend.synthetic_data import create_training_dataset, generate_fake_demand_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = './models'

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class SimpleDemandNet(nn.Module):
    """Simple neural network for demand forecasting."""
    def __init__(self, input_size, hidden_size=64):
        super(SimpleDemandNet, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # x shape: (batch, sequence_length, features)
        lstm_out, _ = self.lstm(x)
        # Take the last output
        last_output = lstm_out[:, -1, :]
        demand = self.fc(last_output)
        return demand

def train_model():
    """Train a simple LSTM model for demand forecasting."""
    logger.info("🔍 Starting Model Training...")
    
    # Generate synthetic data
    sales_df, external_df = generate_fake_demand_data(
        start_date="2023-01-01", 
        end_date="2024-12-31",
        num_products=10,
        num_locations=5
    )
    
    # Create training dataset
    X, y = create_training_dataset(sales_df, external_df, sequence_length=7)
    
    if len(X) == 0:
        logger.error("No training data available!")
        return
    
    # Normalize features
    n_samples, sequence_length, n_features = X.shape
    X_reshaped = X.reshape(-1, n_features)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_reshaped)
    X_scaled = X_scaled.reshape(n_samples, sequence_length, n_features)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).reshape(-1, 1)
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.FloatTensor(y_test).reshape(-1, 1)
    
    # Initialize model
    model = SimpleDemandNet(input_size=n_features)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    n_epochs = 50
    batch_size = 32
    
    logger.info(f"Training on {len(X_train)} samples...")
    
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        
        # Mini-batch training
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train_tensor[i:i+batch_size]
            batch_y = y_train_tensor[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            n_batches += 1
        
        # Validation
        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_outputs = model(X_test_tensor)
                val_loss = criterion(val_outputs, y_test_tensor)
                
            logger.info(f"Epoch [{epoch+1}/{n_epochs}], Train Loss: {epoch_loss/n_batches:.4f}, Val Loss: {val_loss:.4f}")
    
    # Save the trained model
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': n_features,
        'hidden_size': 64
    }, os.path.join(CACHE_DIR, 'pytorch_model.bin'))
    
    # Save the scaler
    joblib.dump(scaler, os.path.join(CACHE_DIR, 'scaler.pkl'))
    
    # Calculate final metrics
    model.eval()
    with torch.no_grad():
        test_predictions = model(X_test_tensor)
        test_mae = torch.mean(torch.abs(test_predictions - y_test_tensor)).item()
        
    logger.info(f"Final Test MAE: {test_mae:.2f}")
    logger.info("✅ Model training completed and saved.")

if __name__ == "__main__":
    train_model()

