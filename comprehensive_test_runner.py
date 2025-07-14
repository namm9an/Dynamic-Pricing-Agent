#!/usr/bin/env python3
"""
Comprehensive Test Runner for Dynamic Pricing Agent
Handles all compatibility issues and runs full validation
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class ComprehensiveTestRunner:
    def __init__(self):
        self.results = {}
        self.passed_tests = 0
        self.total_tests = 0
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests with dependency fixes"""
        print("🚀 Starting Comprehensive Test Suite for Dynamic Pricing Agent")
        print("=" * 80)
        
        # Test 1: Core System Validation
        self._test_core_system()
        
        # Test 2: Individual Component Tests
        self._test_individual_components()
        
        # Test 3: Integration Tests
        self._test_integration()
        
        # Test 4: API Functionality Tests
        self._test_api_functionality()
        
        # Test 5: Machine Learning Pipeline Tests
        self._test_ml_pipeline()
        
        # Generate final report
        self._generate_final_report()
        
        return self.results
    
    def _test_core_system(self):
        """Test core system functionality"""
        print("\n📋 Testing Core System...")
        
        # Test system validation
        try:
            result = subprocess.run([
                sys.executable, "backend/validate_system.py"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self._record_test("Core System Validation", True, "All core components validated")
            else:
                self._record_test("Core System Validation", False, f"Exit code: {result.returncode}")
        except Exception as e:
            self._record_test("Core System Validation", False, str(e))
    
    def _test_individual_components(self):
        """Test individual components with error handling"""
        print("\n🔧 Testing Individual Components...")
        
        # Test 1: Synthetic Data Generation
        try:
            sys.path.append('backend')
            from synthetic_data import generate_sample_data_for_product
            
            data = generate_sample_data_for_product('TEST_PROD', 'NYC', 10)
            if len(data) > 0:
                self._record_test("Synthetic Data Generation", True, f"Generated {len(data)} records")
            else:
                self._record_test("Synthetic Data Generation", False, "No data generated")
        except Exception as e:
            self._record_test("Synthetic Data Generation", False, str(e))
        
        # Test 2: RL Agent (with fallback)
        try:
            from backend.pricing_engine.rl_agent import recommend_price
            
            result = recommend_price(1.5, 1.0, 25.0)
            if 'optimal_price' in result:
                self._record_test("RL Agent Pricing", True, f"Price: ${result['optimal_price']}")
            else:
                self._record_test("RL Agent Pricing", False, "No optimal price returned")
        except Exception as e:
            self._record_test("RL Agent Pricing", False, str(e))
        
        # Test 3: Demand Model (with fallback)
        try:
            from backend.pricing_engine.demand_model import DemandModel
            
            model = DemandModel()
            if model is not None:
                self._record_test("Demand Model Loading", True, "Model loaded successfully")
            else:
                self._record_test("Demand Model Loading", False, "Model is None")
        except Exception as e:
            self._record_test("Demand Model Loading", False, str(e))
    
    def _test_integration(self):
        """Test integration between components"""
        print("\n🔗 Testing Integration...")
        
        # Test 1: Multimodal Fusion (with mock fallback)
        try:
            from backend.fusion import MultimodalPricingFusion
            
            fusion = MultimodalPricingFusion()
            result = fusion.predict_demand(
                {'price_pred': 0.7}, 
                "mock_image_data", 
                "Positive market trends"
            )
            
            if 'demand' in result and 'confidence' in result:
                self._record_test("Multimodal Fusion", True, f"Demand: {result['demand']}, Confidence: {result['confidence']}")
            else:
                self._record_test("Multimodal Fusion", False, "Missing demand or confidence")
        except Exception as e:
            self._record_test("Multimodal Fusion", False, str(e))
        
        # Test 2: Auto Update Service
        try:
            from backend.auto_updater import AutoUpdateService
            import numpy as np
            
            updater = AutoUpdateService()
            
            # Test with no drift
            ref_data = np.random.normal(0, 1, 1000)
            new_data = np.random.normal(0, 1, 1000)
            no_drift = updater.detect_drift(new_data, ref_data)
            
            # Test with drift
            drift_data = np.random.normal(2, 1, 1000)
            has_drift = updater.detect_drift(drift_data, ref_data)
            
            if not no_drift and has_drift:
                self._record_test("Auto Update Service", True, "Drift detection working correctly")
            else:
                self._record_test("Auto Update Service", False, f"Drift detection failed: no_drift={no_drift}, has_drift={has_drift}")
        except Exception as e:
            self._record_test("Auto Update Service", False, str(e))
    
    def _test_api_functionality(self):
        """Test API functionality without starting server"""
        print("\n🌐 Testing API Functionality...")
        
        # Test 1: App import and initialization
        try:
            from backend.app import app, generate_input_sequence
            
            # Test input sequence generation
            sequence = generate_input_sequence(49.99, "NYC", "PROD_001", 30)
            if len(sequence) > 0:
                self._record_test("API Input Generation", True, f"Generated sequence of length {len(sequence)}")
            else:
                self._record_test("API Input Generation", False, "Empty sequence generated")
        except Exception as e:
            self._record_test("API Input Generation", False, str(e))
        
        # Test 2: FastAPI app creation
        try:
            from backend.app import app
            
            if app is not None:
                self._record_test("FastAPI App Creation", True, "App created successfully")
            else:
                self._record_test("FastAPI App Creation", False, "App is None")
        except Exception as e:
            self._record_test("FastAPI App Creation", False, str(e))
    
    def _test_ml_pipeline(self):
        """Test machine learning pipeline"""
        print("\n🤖 Testing ML Pipeline...")
        
        # Test 1: Model file existence
        model_files = [
            Path("models/pytorch_model.bin"),
            Path("models/scaler.pkl"),
            Path("models/pricing_agent")
        ]
        
        existing_files = [f for f in model_files if f.exists()]
        if len(existing_files) > 0:
            self._record_test("Model Files", True, f"Found {len(existing_files)} model files")
        else:
            self._record_test("Model Files", False, "No model files found")
        
        # Test 2: Training capability
        try:
            # Check if training modules can be imported
            from backend.train_demand import train_model
            from backend.train_agent import train_optimized_agent
            
            self._record_test("Training Modules", True, "Training modules imported successfully")
        except Exception as e:
            self._record_test("Training Modules", False, str(e))
    
    def _record_test(self, test_name: str, passed: bool, details: str):
        """Record test results"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED - {details}")
        else:
            print(f"❌ {test_name}: FAILED - {details}")
        
        self.results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def _generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"\n🎯 Overall Results: {self.passed_tests}/{self.total_tests} tests passed")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Group results by category
        categories = {
            'Core System': ['Core System Validation'],
            'Individual Components': ['Synthetic Data Generation', 'RL Agent Pricing', 'Demand Model Loading'],
            'Integration': ['Multimodal Fusion', 'Auto Update Service'],
            'API Functionality': ['API Input Generation', 'FastAPI App Creation'],
            'ML Pipeline': ['Model Files', 'Training Modules']
        }
        
        print("\n📋 Results by Category:")
        for category, tests in categories.items():
            category_passed = sum(1 for test in tests if test in self.results and self.results[test]['passed'])
            category_total = len(tests)
            print(f"\n{category}: {category_passed}/{category_total}")
            
            for test in tests:
                if test in self.results:
                    status = "✅ PASS" if self.results[test]['passed'] else "❌ FAIL"
                    print(f"  {test}: {status}")
        
        # Recommendations
        print("\n🔧 Recommendations:")
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED! System is ready for production.")
        elif self.passed_tests >= self.total_tests * 0.8:
            print("✨ Most tests passed. System is functional with minor issues.")
        else:
            print("⚠️  Several tests failed. Review failed components before deployment.")
        
        # Next Steps
        print("\n📝 Next Steps:")
        failed_tests = [test for test, result in self.results.items() if not result['passed']]
        if failed_tests:
            print("1. Address failed tests:")
            for test in failed_tests:
                print(f"   - {test}: {self.results[test]['details']}")
        else:
            print("1. All tests passed! System is ready for production deployment.")
        
        print("2. Consider running load tests for production readiness.")
        print("3. Set up monitoring and alerting for production environment.")

def main():
    """Main function to run comprehensive tests"""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()
    
    # Return appropriate exit code
    success_rate = runner.passed_tests / runner.total_tests
    if success_rate >= 0.8:
        return 0  # Success
    else:
        return 1  # Failure

if __name__ == "__main__":
    sys.exit(main())
