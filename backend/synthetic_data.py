import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Tuple, List

fake = Faker()

def generate_fake_demand_data(
    start_date: str = "2023-01-01",
    end_date: str = "2024-12-31", 
    num_products: int = 10,
    num_locations: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic historical sales data and external factors.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        num_products: Number of unique products
        num_locations: Number of unique locations
    
    Returns:
        Tuple of (sales_data, external_factors) DataFrames
    """
    
    # Generate date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_range = pd.date_range(start=start, end=end, freq='D')
    
    # Generate product and location lists
    products = [f"PROD_{i:03d}" for i in range(1, num_products + 1)]
    locations = [fake.city() for _ in range(num_locations)]
    
    # Generate sales data
    sales_records = []
    
    for date in date_range:
        # Generate varying number of sales per day (0-50)
        num_sales = random.randint(5, 50)
        
        for _ in range(num_sales):
            product_id = random.choice(products)
            location = random.choice(locations)
            
            # Generate realistic price based on product (with some variance)
            base_price = hash(product_id) % 100 + 20  # Base price 20-120
            price_variance = random.uniform(0.8, 1.2)  # ±20% variance
            price = round(base_price * price_variance, 2)
            
            # Generate demand based on price elasticity and external factors
            # Higher prices = lower demand (basic elasticity)
            base_demand = max(1, int(100 - (price - 20) * 0.5))
            
            # Add seasonality (higher demand in winter months)
            seasonal_factor = 1.2 if date.month in [11, 12, 1, 2] else 1.0
            
            # Add weekend effect (higher demand on weekends)
            weekend_factor = 1.3 if date.weekday() >= 5 else 1.0
            
            # Add random noise
            noise_factor = random.uniform(0.7, 1.3)
            
            units_sold = max(1, int(base_demand * seasonal_factor * weekend_factor * noise_factor))
            
            sales_records.append({
                'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
                'product_id': product_id,
                'price': price,
                'units_sold': units_sold,
                'location': location
            })
    
    sales_df = pd.DataFrame(sales_records)
    
    # Generate external factors data
    external_records = []
    
    for date in date_range:
        # Determine if it's a holiday (simplified - just some random days)
        is_holiday = random.random() < 0.05  # 5% chance of being a holiday
        
        # Generate weather code (0=sunny, 1=cloudy, 2=rainy, 3=snowy)
        # Make winter months more likely to have snow/rain
        if date.month in [12, 1, 2]:
            weather_code = random.choices([0, 1, 2, 3], weights=[20, 30, 30, 20])[0]
        elif date.month in [6, 7, 8]:
            weather_code = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
        else:
            weather_code = random.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
        
        external_records.append({
            'timestamp': date.strftime('%Y-%m-%d %H:%M:%S'),
            'is_holiday': is_holiday,
            'weather_code': weather_code
        })
    
    external_df = pd.DataFrame(external_records)
    
    return sales_df, external_df


def generate_sample_data_for_product(
    product_id: str,
    location: str,
    days: int = 30
) -> pd.DataFrame:
    """
    Generate sample demand data for a specific product and location.
    
    Args:
        product_id: Product identifier
        location: Location name
        days: Number of days of data to generate
    
    Returns:
        DataFrame with sample data for the product
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    records = []
    
    for date in date_range:
        # Generate realistic price variations
        base_price = 50.0  # Base price
        price_trend = np.sin(len(records) * 0.1) * 5  # Cyclical trend
        random_noise = random.uniform(-3, 3)
        price = round(base_price + price_trend + random_noise, 2)
        
        # Generate demand based on price and other factors
        price_elasticity = -0.8  # Elastic demand
        base_demand = 100
        demand = max(1, int(base_demand + (50 - price) * price_elasticity + random.uniform(-10, 10)))
        
        records.append({
            'timestamp': date.strftime('%Y-%m-%d'),
            'product_id': product_id,
            'price': price,
            'units_sold': demand,
            'location': location,
            'is_holiday': random.random() < 0.05,
            'weather_code': random.randint(0, 3)
        })
    
    return pd.DataFrame(records)


def create_training_dataset(
    sales_df: pd.DataFrame,
    external_df: pd.DataFrame,
    sequence_length: int = 7
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training dataset for time series forecasting.
    
    Args:
        sales_df: Sales data DataFrame
        external_df: External factors DataFrame
        sequence_length: Length of input sequences
    
    Returns:
        Tuple of (X, y) arrays for training
    """
    # Merge sales and external data
    merged_df = pd.merge(sales_df, external_df, on='timestamp', how='inner')
    merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
    merged_df = merged_df.sort_values('timestamp')
    
    # Group by product and location
    X_list = []
    y_list = []
    
    for (product_id, location), group in merged_df.groupby(['product_id', 'location']):
        group = group.sort_values('timestamp').reset_index(drop=True)
        
        if len(group) < sequence_length + 1:
            continue
        
        # Create features
        features = ['price', 'units_sold', 'is_holiday', 'weather_code']
        feature_matrix = group[features].values
        
        # Create sequences
        for i in range(len(feature_matrix) - sequence_length):
            X_sequence = feature_matrix[i:i+sequence_length]
            y_target = feature_matrix[i+sequence_length, 1]  # units_sold
            
            X_list.append(X_sequence)
            y_list.append(y_target)
    
    return np.array(X_list), np.array(y_list)


if __name__ == "__main__":
    # Generate and save sample data
    print("Generating synthetic demand data...")
    sales_df, external_df = generate_fake_demand_data()
    
    print(f"Generated {len(sales_df)} sales records")
    print(f"Generated {len(external_df)} external factor records")
    
    # Save to CSV for inspection
    sales_df.to_csv("synthetic_sales_data.csv", index=False)
    external_df.to_csv("synthetic_external_data.csv", index=False)
    
    print("Sample sales data:")
    print(sales_df.head())
    print("\nSample external factors:")
    print(external_df.head())
    
    # Create training dataset
    X, y = create_training_dataset(sales_df, external_df)
    print(f"\nTraining dataset shape: X={X.shape}, y={y.shape}")
