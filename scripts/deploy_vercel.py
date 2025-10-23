#!/usr/bin/env python3
"""
Vercel Deployment Script
Medical Text Classification App

This script prepares and deploys the application to Vercel.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

class VercelDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend"
        self.api_dir = self.project_root / "api"
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check if Vercel CLI is installed
        try:
            result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Vercel CLI installed: {result.stdout.strip()}")
            else:
                print("❌ Vercel CLI not found. Install with: npm i -g vercel")
                return False
        except FileNotFoundError:
            print("❌ Vercel CLI not found. Install with: npm i -g vercel")
            return False
        
        # Check if Node.js is installed
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js installed: {result.stdout.strip()}")
            else:
                print("❌ Node.js not found. Please install Node.js 18+")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js 18+")
            return False
        
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        print("✅ Frontend directory found")
        
        # Check if API directory exists
        if not self.api_dir.exists():
            print("❌ API directory not found")
            return False
        print("✅ API directory found")
        
        # Check if vercel.json exists
        vercel_config = self.project_root / "vercel.json"
        if not vercel_config.exists():
            print("❌ vercel.json not found")
            return False
        print("✅ vercel.json found")
        
        return True
    
    def prepare_frontend(self):
        """Prepare frontend for deployment."""
        print("\n🔧 Preparing frontend...")
        
        # Check if package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ Frontend package.json not found")
            return False
        
        # Install dependencies
        print("📦 Installing frontend dependencies...")
        try:
            result = subprocess.run(
                ["npm", "ci"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
            print("✅ Frontend dependencies installed")
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
        
        # Build frontend
        print("🏗️ Building frontend...")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to build frontend: {result.stderr}")
                return False
            print("✅ Frontend built successfully")
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            return False
        
        return True
    
    def prepare_api(self):
        """Prepare API for deployment."""
        print("\n🔧 Preparing API...")
        
        # Check if main.py exists
        main_py = self.api_dir / "main.py"
        if not main_py.exists():
            print("❌ API main.py not found")
            return False
        print("✅ API main.py found")
        
        # Check if requirements.txt exists
        requirements = self.api_dir / "requirements.txt"
        if not requirements.exists():
            print("❌ API requirements.txt not found")
            return False
        print("✅ API requirements.txt found")
        
        return True
    
    def check_environment_variables(self):
        """Check and display environment variables."""
        print("\n🌍 Environment Variables:")
        
        env_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "INFO"
        }
        
        print("Required environment variables for Vercel:")
        for key, default in env_vars.items():
            print(f"  {key}={default}")
        
        print("\n💡 Set these in Vercel dashboard: Project Settings → Environment Variables")
        return True
    
    def deploy_to_vercel(self, production=True):
        """Deploy to Vercel."""
        print(f"\n🚀 Deploying to Vercel ({'production' if production else 'preview'})...")
        
        try:
            # Prepare deployment command
            cmd = ["vercel"]
            if production:
                cmd.append("--prod")
            
            # Run deployment
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Deployment successful!")
                print(f"📄 Output:\n{result.stdout}")
                
                # Extract deployment URL
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'https://' in line and 'vercel.app' in line:
                        print(f"🌐 Deployment URL: {line.strip()}")
                        break
                
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            return False
    
    def run_deployment(self, production=True):
        """Run complete deployment process."""
        print("🚀 Starting Vercel deployment process...")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Please fix the issues above.")
            return False
        
        # Prepare frontend
        if not self.prepare_frontend():
            print("\n❌ Frontend preparation failed.")
            return False
        
        # Prepare API
        if not self.prepare_api():
            print("\n❌ API preparation failed.")
            return False
        
        # Check environment variables
        self.check_environment_variables()
        
        # Deploy to Vercel
        if not self.deploy_to_vercel(production):
            print("\n❌ Deployment failed.")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Configure environment variables in Vercel dashboard")
        print("2. Set up custom domain (optional)")
        print("3. Configure monitoring and analytics")
        print("4. Test the deployed application")
        
        return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Medical Text Classification to Vercel")
    parser.add_argument("--preview", action="store_true", help="Deploy to preview environment")
    parser.add_argument("--check-only", action="store_true", help="Only check prerequisites")
    
    args = parser.parse_args()
    
    deployer = VercelDeployer()
    
    if args.check_only:
        success = deployer.check_prerequisites()
        sys.exit(0 if success else 1)
    
    production = not args.preview
    success = deployer.run_deployment(production)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
