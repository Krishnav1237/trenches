#!/usr/bin/env python3
"""
Twitter API Troubleshooting Guide
"""

print("🐦 Twitter API Troubleshooting Guide")
print("=" * 40)

print("\n❌ Getting '401 Unauthorized' Error")
print("\nThis usually means one of these issues:")

print("\n1. 🔑 CREDENTIALS ISSUE:")
print("   • Your API keys/tokens are incorrect")
print("   • Your tokens have expired")
print("   • You copied them incorrectly")

print("\n2. 🛡️  PERMISSIONS ISSUE:")
print("   • Your app doesn't have 'Read and Write' permissions")
print("   • You need to regenerate tokens after changing permissions")

print("\n3. 🏗️  APP CONFIGURATION ISSUE:")
print("   • Your app is in 'Development' mode with restrictions")
print("   • You haven't set up OAuth properly")

print("\n📋 STEP-BY-STEP FIX:")
print("=" * 30)

print("\n🔧 Step 1: Check App Permissions")
print("   1. Go to https://developer.twitter.com/en/portal/dashboard")
print("   2. Click on your app")
print("   3. Go to 'Settings' tab")
print("   4. Ensure 'App permissions' is set to 'Read and write'")
print("   5. If you changed it, you MUST regenerate your Access Tokens!")

print("\n🔧 Step 2: Regenerate Tokens")
print("   1. In your app dashboard, go to 'Keys and tokens' tab")
print("   2. Under 'Access Token and Secret', click 'Regenerate'")
print("   3. Copy the NEW tokens (they'll be different)")
print("   4. Update your .env file with the new tokens")

print("\n🔧 Step 3: Verify App Type")
print("   1. Make sure your app type supports what you need")
print("   2. If using 'Essential' access, you have limitations")
print("   3. Consider upgrading to 'Elevated' access if needed")

print("\n🔧 Step 4: Test Individual Components")
print("   1. Test Bearer Token first (read-only)")
print("   2. Then test with Access Tokens (read-write)")

print("\n💡 COMMON MISTAKES:")
print("   • Copying tokens with extra spaces or characters")
print("   • Using old tokens after changing permissions")
print("   • Having quotes around tokens in .env file")
print("   • URL-encoded characters in Bearer Token")

print("\n🎯 NEXT STEPS:")
print("1. Go fix your app permissions")
print("2. Regenerate your Access Tokens")
print("3. Update your .env file")
print("4. Run: python debug_twitter.py")

print("\n📞 If still having issues:")
print("   • Check Twitter Developer Platform status")
print("   • Verify your account is in good standing")
print("   • Try creating a new app if the old one is problematic")

print("\n" + "=" * 50)
print("🚀 Once fixed, run: python enhanced_simulation.py")
print("=" * 50)