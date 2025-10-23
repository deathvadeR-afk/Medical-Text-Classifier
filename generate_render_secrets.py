#!/usr/bin/env python3
"""
Generate secure secrets for Render deployment.
Run this script to generate the SECRET_KEY and API_KEYS needed for production.
"""
import secrets

def generate_secrets():
    """Generate secure secrets for production deployment."""
    print("🔐 Generating secure secrets for Render deployment...\n")
    
    # Generate SECRET_KEY (64+ characters for JWT)
    secret_key = secrets.token_urlsafe(64)
    print("SECRET_KEY (copy this to Render environment variables):")
    print(f"SECRET_KEY={secret_key}")
    print()
    
    # Generate API_KEYS (3 keys for different clients)
    api_keys = [secrets.token_urlsafe(32) for _ in range(3)]
    api_keys_str = ",".join(api_keys)
    print("API_KEYS (copy this to Render environment variables):")
    print(f"API_KEYS={api_keys_str}")
    print()
    
    # Individual API keys for reference
    print("Individual API Keys (for testing/client distribution):")
    for i, key in enumerate(api_keys, 1):
        print(f"API_KEY_{i}={key}")
    print()
    
    # Test curl command
    print("🧪 Test command (replace YOUR_API_URL with actual Render URL):")
    print(f'curl -X POST "YOUR_API_URL/predict" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -H "X-API-Key: {api_keys[0]}" \\')
    print(f'  -d \'{{"text": "What are the symptoms of diabetes?"}}\'')
    print()
    
    print("✅ Secrets generated successfully!")
    print("📋 Copy the SECRET_KEY and API_KEYS values to your Render environment variables.")

if __name__ == "__main__":
    generate_secrets()
