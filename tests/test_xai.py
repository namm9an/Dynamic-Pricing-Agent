"""
Test file for Explainable AI Service
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from backend.xai_service import ExplainablePricingAI


def test_xai():
    """Test the ExplainablePricingAI"""
    print("Testing Explainable AI Service...")
    
    try:
        # Mock data for testing
        features = np.random.rand(1, 10)
        prediction = 0.75
        
        # Initialize the XAI service
        xai = ExplainablePricingAI()
        
        # Test explanation generation
        result = xai.generate_explanation(features, prediction)
        
        # Check if required fields are present
        assert 'shap_waterfall' in result, "SHAP waterfall missing"
        assert 'feature_importance' in result, "Feature importance missing"
        assert 'counterfactuals' in result, "Counterfactuals missing"
        
        print("XAI Test Results:")
        print(f"Feature Importance: {len(result['feature_importance'])} features")
        print(f"Counterfactual Scenarios: {len(result['counterfactuals']['scenarios'])}")
        
        print("Explainable AI service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error in XAI test: {e}")
        return False


if __name__ == "__main__":
    test_xai()
