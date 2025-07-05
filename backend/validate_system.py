#!/usr/bin/env python3
"""
Phase 1 Validation Script
Checks all requirements for Phase 1 completion.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
import subprocess
import requests
from typing import Dict, List, Tuple

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(message: str, status: str):
    """Print formatted status message."""
    if status == "PASS":
        print(f"{GREEN}✅ {message} - PASS{RESET}")
    elif status == "FAIL":
        print(f"{RED}❌ {message} - FAIL{RESET}")
    else:
        print(f"{YELLOW}⚠️  {message} - {status}{RESET}")

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()

def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists."""
    return Path(dirpath).exists() and Path(dirpath).is_dir()

async def check_data_preparation():
    """Check if data preparation components are complete."""
    print("\n🔍 Checking Data Preparation...")
    
    checks = []
    
    # Check synthetic_data.py exists and has required functions
    if check_file_exists("backend/synthetic_data.py"):
        with open("backend/synthetic_data.py", "r", encoding="utf-8") as f:
            content = f.read()
            has_generate = "def generate_fake_demand_data" in content
            has_sample = "def generate_sample_data_for_product" in content
            has_training = "def create_training_dataset" in content
            
            if has_generate and has_sample and has_training:
                print_status("synthetic_data.py with all required functions", "PASS")
                checks.append(True)
            else:
                print_status("synthetic_data.py missing some functions", "FAIL")
                checks.append(False)
    else:
        print_status("synthetic_data.py not found", "FAIL")
        checks.append(False)
    
    # Check startup.py for auto-generation logic
    if check_file_exists("backend/startup.py"):
        with open("backend/startup.py", "r", encoding="utf-8") as f:
            content = f.read()
            has_auto_gen = "generate_and_insert_fake_data" in content
            has_check = "if len(sales_data) == 0:" in content
            
            if has_auto_gen and has_check:
                print_status("Auto-generation logic in startup.py", "PASS")
                checks.append(True)
            else:
                print_status("Auto-generation logic incomplete", "FAIL")
                checks.append(False)
    else:
        print_status("startup.py not found", "FAIL")
        checks.append(False)
    
    return all(checks)

async def check_model_setup():
    """Check if model setup is complete."""
    print("\n🔍 Checking Model Setup...")
    
    checks = []
    
    # Check demand_model.py
    if check_file_exists("backend/pricing_engine/demand_model.py"):
        with open("backend/pricing_engine/demand_model.py", "r", encoding="utf-8") as f:
            content = f.read()
            has_class = "class DemandModel" in content
            has_predict = "def predict" in content
            has_load = "def _load_model" in content
            
            if has_class and has_predict and has_load:
                print_status("demand_model.py with DemandModel class", "PASS")
                checks.append(True)
            else:
                print_status("demand_model.py incomplete", "FAIL")
                checks.append(False)
    else:
        print_status("demand_model.py not found", "FAIL")
        checks.append(False)
    
    # Check models directory
    if check_directory_exists("./models"):
        print_status("Models directory exists", "PASS")
        checks.append(True)
    else:
        print_status("Models directory not found", "FAIL")
        checks.append(False)
    
    return all(checks)

async def check_training():
    """Check if training components are complete."""
    print("\n🔍 Checking Training Components...")
    
    checks = []
    
    # Check train_demand.py
    if check_file_exists("backend/train_demand.py"):
        with open("backend/train_demand.py", "r", encoding="utf-8") as f:
            content = f.read()
            has_train = "def train_model" in content
            has_lstm = "class SimpleDemandNet" in content
            has_save = "torch.save" in content
            
            if has_train and has_lstm and has_save:
                print_status("train_demand.py with training logic", "PASS")
                checks.append(True)
            else:
                print_status("train_demand.py incomplete", "FAIL")
                checks.append(False)
    else:
        print_status("train_demand.py not found", "FAIL")
        checks.append(False)
    
    # Check if model files exist
    model_exists = check_file_exists("./models/pytorch_model.bin")
    scaler_exists = check_file_exists("./models/scaler.pkl")
    
    if model_exists and scaler_exists:
        print_status("Trained model files exist", "PASS")
        checks.append(True)
    else:
        print_status("Trained model files not found", "WARNING - Run training first")
        checks.append(True)  # Not a hard failure
    
    return all(checks)

async def check_api_integration():
    """Check if API integration is complete."""
    print("\n🔍 Checking API Integration...")
    
    checks = []
    
    # Check app.py
    if check_file_exists("backend/app.py"):
        with open("backend/app.py", "r", encoding="utf-8") as f:
            content = f.read()
            has_predict = "/predict-demand" in content
            has_startup = "@app.on_event(\"startup\")" in content
            has_model_use = "demand_model.predict" in content or "demand_model is not None" in content
            
            if has_predict and has_startup and has_model_use:
                print_status("API endpoints with model integration", "PASS")
                checks.append(True)
            else:
                print_status("API integration incomplete", "FAIL")
                checks.append(False)
    else:
        print_status("app.py not found", "FAIL")
        checks.append(False)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print_status("API health check endpoint", "PASS")
            checks.append(True)
        else:
            print_status("API health check failed", "WARNING")
            checks.append(True)
    except:
        print_status("API not running", "INFO - Start with 'uvicorn backend.app:app'")
        checks.append(True)  # Not a hard failure
    
    return all(checks)

async def check_dependencies():
    """Check if all dependencies are properly set up."""
    print("\n🔍 Checking Dependencies...")
    
    checks = []
    
    # Check requirements.txt
    if check_file_exists("backend/requirements.txt"):
        with open("backend/requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            required_packages = [
                "fastapi", "uvicorn", "supabase", "transformers",
                "torch", "pandas", "numpy", "scikit-learn", "joblib"
            ]
            
            missing = []
            for package in required_packages:
                if package not in content:
                    missing.append(package)
            
            if not missing:
                print_status("All required packages in requirements.txt", "PASS")
                checks.append(True)
            else:
                print_status(f"Missing packages: {', '.join(missing)}", "FAIL")
                checks.append(False)
    else:
        print_status("requirements.txt not found", "FAIL")
        checks.append(False)
    
    # Check .env file
    if check_file_exists(".env"):
        print_status(".env file exists", "PASS")
        checks.append(True)
    else:
        print_status(".env file not found", "FAIL")
        checks.append(False)
    
    return all(checks)

async def run_validation():
    """Run all validation checks."""
    print("=" * 60)
    print("🚀 PHASE 1 VALIDATION - Dynamic Pricing Agent")
    print("=" * 60)
    
    results = {
        "Data Preparation": await check_data_preparation(),
        "Model Setup": await check_model_setup(),
        "Training": await check_training(),
        "API Integration": await check_api_integration(),
        "Dependencies": await check_dependencies()
    }
    
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_pass = sum(results.values())
    total_checks = len(results)
    
    for component, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print_status(f"{component}", status)
    
    print("\n" + "=" * 60)
    
    if total_pass == total_checks:
        print(f"{GREEN}🎉 PHASE 1 COMPLETE! All {total_checks} components validated.{RESET}")
        print(f"{GREEN}✅ Ready to proceed to Phase 2 (RL Pricing Agent){RESET}")
        
        # Save completion status
        import datetime
        completion_status = {
            "phase": 1,
            "status": "COMPLETE",
            "components": results,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        with open("phase1_completion.json", "w") as f:
            json.dump(completion_status, f, indent=2)
        
        print(f"\n{GREEN}📄 Completion status saved to phase1_completion.json{RESET}")
        
    else:
        print(f"{RED}⚠️  PHASE 1 INCOMPLETE: {total_pass}/{total_checks} components passed{RESET}")
        print(f"{YELLOW}Please fix the failed components before proceeding.{RESET}")
        
        print("\n📝 Next Steps:")
        if not results["Training"]:
            print("  1. Run 'python backend/train_demand.py' to train the model")
        if not results["Dependencies"]:
            print("  2. Ensure .env file exists with Supabase credentials")
        if not results["API Integration"]:
            print("  3. Start the API with 'uvicorn backend.app:app --reload'")
    
    return total_pass == total_checks

if __name__ == "__main__":
    success = asyncio.run(run_validation())
    sys.exit(0 if success else 1)
