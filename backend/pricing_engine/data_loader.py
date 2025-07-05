import pandas as pd
from backend.database import get_sales_data, get_external_factors

async def fetch_and_merge_data(start_date, end_date):
    """Fetches and merges sales data with external factors."""
    sales_data = await get_sales_data(start_date, end_date)
    factors_data = await get_external_factors(start_date, end_date)
    merged_data = pd.merge(sales_data, factors_data, on='timestamp', how='inner')
    return merged_data

