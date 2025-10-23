#!/usr/bin/env python3
"""
Test runner script for Medical Text Classification project.
Provides unified interface for running different types of tests.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description or cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description or cmd} completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or cmd} failed with exit code {e.returncode}")
        return e.returncode


def setup_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["MODEL_PATH"] = "models"
    
    # Set database URL if not already set
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_medical_text_db"
    
    print("🔧 Environment variables set for testing")


def create_mock_models():
    """Create mock model files for testing."""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Create label mapping files
    reverse_mapping = {
        "0": "Neurological & Cognitive Disorders",
        "1": "Cancers", 
        "2": "Cardiovascular Diseases",
        "3": "Metabolic & Endocrine Disorders",
        "4": "Other Age-Related & Immune Disorders"
    }
    
    label_mapping = {v: k for k, v in reverse_mapping.items()}
    
    import json
    with open(models_dir / "reverse_label_mapping.json", "w") as f:
        json.dump(reverse_mapping, f, indent=2)
    
    with open(models_dir / "label_mapping.json", "w") as f:
        json.dump(label_mapping, f, indent=2)
    
    print("🔧 Mock model files created")


def run_unit_tests(coverage=False, html=False):
    """Run unit tests."""
    cmd = "python -m pytest tests/unit -v"
    
    if coverage:
        cmd += " --cov=src --cov-report=xml"
        if html:
            cmd += " --cov-report=html"
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(coverage=False, html=False):
    """Run integration tests."""
    cmd = "python -m pytest tests/integration -v"
    
    if coverage:
        cmd += " --cov=src --cov-report=xml"
        if html:
            cmd += " --cov-report=html"
    
    return run_command(cmd, "Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests."""
    cmd = "python -m pytest tests/e2e -v"
    return run_command(cmd, "End-to-End Tests")


def run_performance_tests():
    """Run performance tests."""
    cmd = "python -m pytest tests/performance -v"
    return run_command(cmd, "Performance Tests")


def run_security_tests():
    """Run security tests."""
    cmd = "python -m pytest tests/security -v"
    return run_command(cmd, "Security Tests")


def run_all_tests(coverage=False, html=False):
    """Run all tests."""
    exit_codes = []
    
    # Run different test suites
    exit_codes.append(run_unit_tests(coverage, html))
    exit_codes.append(run_integration_tests(coverage, html))
    
    # Only run these if directories exist
    if Path("tests/e2e").exists():
        exit_codes.append(run_e2e_tests())
    
    if Path("tests/performance").exists():
        exit_codes.append(run_performance_tests())
    
    if Path("tests/security").exists():
        exit_codes.append(run_security_tests())
    
    # Return non-zero if any test failed
    return max(exit_codes) if exit_codes else 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Medical Text Classification project")
    
    # Test type arguments
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Coverage arguments
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    
    # Setup arguments
    parser.add_argument("--setup-only", action="store_true", help="Only setup environment and mock files")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    create_mock_models()
    
    if args.setup_only:
        print("✅ Setup completed")
        return 0
    
    # Determine which tests to run
    exit_code = 0
    
    if args.unit:
        exit_code = run_unit_tests(args.coverage, args.html)
    elif args.integration:
        exit_code = run_integration_tests(args.coverage, args.html)
    elif args.e2e:
        exit_code = run_e2e_tests()
    elif args.performance:
        exit_code = run_performance_tests()
    elif args.security:
        exit_code = run_security_tests()
    elif args.all:
        exit_code = run_all_tests(args.coverage, args.html)
    else:
        # Default: run unit and integration tests
        print("No specific test type specified, running unit and integration tests...")
        exit_codes = []
        exit_codes.append(run_unit_tests(args.coverage, args.html))
        exit_codes.append(run_integration_tests(args.coverage, args.html))
        exit_code = max(exit_codes) if exit_codes else 0
    
    if exit_code == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
