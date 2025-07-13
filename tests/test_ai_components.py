"""
Simple Integration Test for AI Components
Tests the core functionality without complex dependencies
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

def test_fusion():
    """Test the fusion component with mock data"""
    print("Testing Multimodal Pricing Fusion...")
    
    try:
        from backend.fusion import MultimodalPricingFusion
        
        # Mock data for testing
        price_data = {'price_pred': 0.7}
        image_data = "mock_image_data"
        trend_data = "Positive market trends for product"
        
        # Initialize and test
        fusion = MultimodalPricingFusion()
        result = fusion.predict_demand(price_data, image_data, trend_data)
        
        assert 'demand' in result, "Demand prediction missing"
        assert 'confidence' in result, "Confidence missing"
        
        print(f"✓ Fusion - Demand: {result['demand']}, Confidence: {result['confidence']}")
        return True
        
    except Exception as e:
        print(f"✗ Fusion test failed: {e}")
        return False

def test_orchestrator():
    """Test the orchestrator component"""
    print("Testing Pricing Orchestrator...")
    
    try:
        from backend.agents.orchestrator import PricingOrchestrator
        
        # Initialize orchestrator
        orchestrator = PricingOrchestrator()
        
        # Basic initialization test
        assert hasattr(orchestrator, '_create_data_agent'), "Missing _create_data_agent method"
        assert hasattr(orchestrator, '_create_pricing_agent'), "Missing _create_pricing_agent method"
        assert hasattr(orchestrator, '_create_crew'), "Missing _create_crew method"
        
        print("✓ Orchestrator initialization successful")
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator test failed: {e}")
        return False

def test_auto_updater():
    """Test the auto updater component"""
    print("Testing Auto Update Service...")
    
    try:
        from backend.auto_updater import AutoUpdateService
        import numpy as np
        
        # Initialize service
        updater = AutoUpdateService()
        
        # Test drift detection with mock data
        reference_data = np.random.normal(0, 1, 1000)
        new_data_no_drift = np.random.normal(0, 1, 1000)
        new_data_with_drift = np.random.normal(2, 1, 1000)  # Shifted mean
        
        # Test no drift
        no_drift = updater.detect_drift(new_data_no_drift, reference_data)
        
        # Test with drift
        has_drift = updater.detect_drift(new_data_with_drift, reference_data)
        
        print(f"✓ Auto Updater - No drift detected: {not no_drift}, Drift detected: {has_drift}")
        return True
        
    except Exception as e:
        print(f"✗ Auto Updater test failed: {e}")
        return False

def test_tools():
    """Test the tools components"""
    print("Testing Tools...")
    
    try:
        from backend.tools.twitter_scraper import TwitterScraperTool
        from backend.tools.calendar_collector import CalendarCollectorTool
        
        # Test tool initialization
        twitter_tool = TwitterScraperTool()
        calendar_tool = CalendarCollectorTool()
        
        assert hasattr(twitter_tool, '_run'), "TwitterScraperTool missing _run method"
        assert hasattr(calendar_tool, '_run'), "CalendarCollectorTool missing _run method"
        
        print("✓ Tools initialization successful")
        return True
        
    except Exception as e:
        print(f"✗ Tools test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AI COMPONENTS INTEGRATION TEST")
    print("=" * 50)
    
    tests = [
        test_fusion,
        test_orchestrator,
        test_auto_updater,
        test_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
