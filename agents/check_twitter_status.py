#!/usr/bin/env python3
"""
Check Your Exact Twitter API Status
"""

print("🔍 CHECKING YOUR TWITTER API STATUS")
print("=" * 50)

print("\n📋 STEP 1: Check Your Access Level")
print("1. Go to: https://developer.twitter.com/en/portal/dashboard")
print("2. Click on your app")
print("3. Look for 'Access Level' - what does it say?")
print("   • Essential = Cannot post tweets")
print("   • Elevated = Can post tweets")
print("   • Premium = Full access")

print("\n📋 STEP 2: Check App Permissions")
print("1. In your app, go to 'Settings' tab")
print("2. Look at 'App permissions' - what does it say?")
print("   • Read = Cannot post")
print("   • Read and Write = Can post")

print("\n📋 STEP 3: Check Keys Generation")
print("1. Go to 'Keys and tokens' tab")
print("2. When did you generate your Access Tokens?")
print("3. If you changed permissions, you MUST regenerate tokens!")

print("\n🎯 MOST LIKELY SCENARIOS:")

print("\n🔄 Scenario 1: You have Essential access")
print("   • Solution: Apply for Elevated (free)")
print("   • Link: https://developer.twitter.com/en/portal/petition/essential/basic-info")

print("\n🔄 Scenario 2: You have Elevated but wrong permissions")
print("   • Go to Settings → Change to 'Read and Write'")
print("   • Go to Keys → Regenerate Access Tokens")
print("   • Update your .env file with new tokens")

print("\n🔄 Scenario 3: You have everything but old tokens")
print("   • Regenerate all tokens")
print("   • Update .env file")
print("   • Test again")

print("\n❓ TELL ME WHAT YOU SEE:")
print("After checking your dashboard, tell me:")
print("1. What's your Access Level? (Essential/Elevated/Premium)")
print("2. What are your App Permissions? (Read/Read and Write)")
print("3. When were your tokens last generated?")

print("\n🚀 ONCE YOU TELL ME, I'LL GIVE YOU EXACT STEPS!")