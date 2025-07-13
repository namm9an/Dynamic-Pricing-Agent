"""
Verification Script for Dynamic Pricing Agent AI Enhancements
Verifies that all required components have been implemented according to specifications
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print result"""
    if Path(file_path).exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} - MISSING")
        return False

def check_class_methods(module_path: str, class_name: str, required_methods: list) -> bool:
    """Check if a class has required methods"""
    try:
        sys.path.append(str(Path(__file__).parent))
        
        # Import module dynamically
        module_name = module_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        if module_name.startswith('.'):
            module_name = module_name[1:]
        
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(cls, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print(f"✓ {class_name} has all required methods: {required_methods}")
            return True
        else:
            print(f"✗ {class_name} missing methods: {missing_methods}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking {class_name}: {e}")
        return False

def verify_requirements():
    """Verify requirements.txt has exact versions"""
    print("\n=== REQUIREMENTS VERIFICATION ===")
    
    required_packages = {
        'crewai==0.28.0': False,
        'snscrape==0.7.0.20230622': False,
        'google-api-python-client==2.108.0': False,
        'transformers==4.35.0': False,
        'torch==2.1.0': False,
        'shap==0.43.0': False
    }
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
        for package in required_packages:
            if package in content:
                required_packages[package] = True
                print(f"✓ {package}")
            else:
                print(f"✗ {package} - MISSING")
                
    except FileNotFoundError:
        print("✗ requirements.txt not found")
        return False
    
    return all(required_packages.values())

def verify_file_structure():
    """Verify mandatory file structure"""
    print("\n=== FILE STRUCTURE VERIFICATION ===")
    
    required_files = [
        ("backend/agents/orchestrator.py", "PricingOrchestrator implementation"),
        ("backend/tools/twitter_scraper.py", "TwitterScraperTool implementation"),
        ("backend/tools/calendar_collector.py", "CalendarCollectorTool implementation"),
        ("backend/fusion.py", "MultimodalPricingFusion implementation"),
        ("backend/xai_service.py", "ExplainablePricingAI implementation"),
        ("backend/auto_updater.py", "AutoUpdateService implementation"),
        ("backend/tools/__init__.py", "Tools package init"),
        ("backend/agents/__init__.py", "Agents package init"),
    ]
    
    passed = 0
    for file_path, description in required_files:
        if check_file_exists(file_path, description):
            passed += 1
    
    print(f"\nFile Structure: {passed}/{len(required_files)} files present")
    return passed == len(required_files)

def verify_class_implementations():
    """Verify class implementations have required methods"""
    print("\n=== CLASS IMPLEMENTATION VERIFICATION ===")
    
    class_checks = [
        ("backend/agents/orchestrator.py", "PricingOrchestrator", 
         ["_create_data_agent", "_create_pricing_agent", "_create_crew"]),
        ("backend/fusion.py", "MultimodalPricingFusion", 
         ["predict_demand"]),
        ("backend/xai_service.py", "ExplainablePricingAI", 
         ["generate_explanation"]),
        ("backend/auto_updater.py", "AutoUpdateService", 
         ["detect_drift"]),
    ]
    
    passed = 0
    for module_path, class_name, methods in class_checks:
        if check_class_methods(module_path, class_name, methods):
            passed += 1
    
    print(f"\nClass Implementation: {passed}/{len(class_checks)} classes verified")
    return passed == len(class_checks)

def verify_environment():
    """Verify environment configuration"""
    print("\n=== ENVIRONMENT VERIFICATION ===")
    
    required_env_vars = [
        "TWITTER_BEARER_TOKEN",
        "GOOGLE_CALENDAR_API_KEY",
        "SUPABASE_URL",
        "NEXT_PUBLIC_API_URL"
    ]
    
    env_file_exists = Path('.env').exists()
    print(f"{'✓' if env_file_exists else '✗'} .env file exists")
    
    if env_file_exists:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        found_vars = 0
        for var in required_env_vars:
            if var in env_content:
                print(f"✓ {var} configured")
                found_vars += 1
            else:
                print(f"✗ {var} missing")
        
        print(f"\nEnvironment: {found_vars}/{len(required_env_vars)} variables configured")
        return found_vars == len(required_env_vars)
    
    return False

def main():
    """Run all verifications"""
    print("=" * 60)
    print("DYNAMIC PRICING AGENT - AI ENHANCEMENTS VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Run all verification checks
    results.append(("Requirements", verify_requirements()))
    results.append(("File Structure", verify_file_structure()))
    results.append(("Class Implementations", verify_class_implementations()))
    results.append(("Environment", verify_environment()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOVERALL RESULT: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATION CHECKS PASSED!")
        print("✨ AI Enhancements implementation is COMPLETE!")
        return True
    else:
        print(f"\n❌ {total - passed} verification checks failed")
        print("🔧 Please address the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
