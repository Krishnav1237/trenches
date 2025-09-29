#!/usr/bin/env python3
"""
Update Twitter Credentials Helper
"""

import os
from pathlib import Path

def update_twitter_credentials():
    """Interactive script to update Twitter credentials"""
    
    print("🔑 Twitter Credentials Update Helper")
    print("=" * 40)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    print("📋 Please enter your NEW regenerated Twitter credentials:")
    print("(Copy them exactly from your Twitter Developer Portal)")
    print()
    
    # Get new credentials
    new_creds = {}
    
    print("🔸 Twitter API Key (Consumer Key):")
    new_creds['TWITTER_API_KEY'] = input().strip()
    
    print("🔸 Twitter API Secret (Consumer Secret):")
    new_creds['TWITTER_API_SECRET'] = input().strip()
    
    print("🔸 Twitter Access Token:")
    new_creds['TWITTER_ACCESS_TOKEN'] = input().strip()
    
    print("🔸 Twitter Access Token Secret:")
    new_creds['TWITTER_ACCESS_TOKEN_SECRET'] = input().strip()
    
    print("🔸 Twitter Bearer Token:")
    new_creds['TWITTER_BEARER_TOKEN'] = input().strip()
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update Twitter credentials
    updated_lines = []
    for line in lines:
        line_updated = False
        for key, value in new_creds.items():
            if line.strip().startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                line_updated = True
                break
        
        if not line_updated:
            updated_lines.append(line)
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("\n✅ Credentials updated in .env file!")
    print("\n🧪 Testing connection...")
    
    # Test the connection
    os.system("python debug_twitter.py")

if __name__ == "__main__":
    update_twitter_credentials()