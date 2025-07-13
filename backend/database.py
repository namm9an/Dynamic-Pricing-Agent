from supabase import create_client, Client
from functools import lru_cache
from dotenv import load_dotenv
import os
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")


def _init_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Return a singleton Supabase client to reuse connections across requests."""
    return _init_client()


async def get_sales_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """Fetch historical sales data from Supabase.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with sales data
    """
    try:
        supabase = get_client()
        query = supabase.table('historical_sales').select('*')
        
        if start_date:
            query = query.gte('timestamp', start_date)
        if end_date:
            query = query.lte('timestamp', end_date)
            
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching sales data: {e}")
        return pd.DataFrame()


async def get_external_factors(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """Fetch external factors data from Supabase.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with external factors data
    """
    try:
        supabase = get_client()
        query = supabase.table('external_factors').select('*')
        
        if start_date:
            query = query.gte('timestamp', start_date)
        if end_date:
            query = query.lte('timestamp', end_date)
            
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching external factors: {e}")
        return pd.DataFrame()


async def insert_sales_data(data: Dict[str, Any]) -> bool:
    """Insert sales data into Supabase.
    
    Args:
        data: Dictionary containing sales data
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_client()
        response = supabase.table('historical_sales').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error inserting sales data: {e}")
        return False


async def insert_external_factors(data: Dict[str, Any]) -> bool:
    """Insert external factors data into Supabase.
    
    Args:
        data: Dictionary containing external factors data
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_client()
        response = supabase.table('external_factors').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error inserting external factors: {e}")
        return False


async def get_feedback_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """Fetch feedback data from Supabase.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with feedback data
    """
    try:
        supabase = get_client()
        query = supabase.table('feedback_data').select('*')
        
        if start_date:
            query = query.gte('timestamp', start_date)
        if end_date:
            query = query.lte('timestamp', end_date)
            
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching feedback data: {e}")
        return pd.DataFrame()


async def get_feedback_count_since(since_date: datetime) -> int:
    """Get count of feedback records since a specific date.
    
    Args:
        since_date: Date to count from
    
    Returns:
        Number of feedback records since the date
    """
    try:
        supabase = get_client()
        response = supabase.table('feedback_data').select('id', count='exact').gte('timestamp', since_date.isoformat()).execute()
        return response.count or 0
    except Exception as e:
        print(f"Error counting feedback data: {e}")
        return 0


async def save_model_version(model_type: str, version: str, file_path: str, metrics: Dict[str, Any]) -> bool:
    """Save model version information to Supabase.
    
    Args:
        model_type: Type of model (e.g., 'demand', 'rl_agent')
        version: Version identifier
        file_path: Path to model file
        metrics: Performance metrics
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_client()
        data = {
            'model_type': model_type,
            'version': version,
            'file_path': file_path,
            'metrics': metrics,
            'created_at': datetime.now().isoformat()
        }
        response = supabase.table('model_versions').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error saving model version: {e}")
        return False


async def insert_feedback_data(data: Dict[str, Any]) -> bool:
    """Insert feedback data into Supabase.
    
    Args:
        data: Dictionary containing feedback data
    
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_client()
        response = supabase.table('feedback_data').insert(data).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error inserting feedback data: {e}")
        return False
