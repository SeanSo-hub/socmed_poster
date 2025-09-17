import requests
import tweepy
import os
from dotenv import load_dotenv
import fb_script
import instagram_script

load_dotenv()

def test_internet_connection():
    """Test basic internet connectivity"""
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ Basic internet connection: OK")
            return True
    except Exception as e:
        print(f"❌ Internet connection failed: {e}")
    return False

def test_facebook_api_reach():
    """Test if we can reach Facebook's Graph API servers"""
    try:
        response = requests.get("https://graph.facebook.com/", timeout=10)
        print(f"✅ Facebook Graph API reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Facebook Graph API: {e}")
    return False

def test_instagram_api_reach():
    """Test if we can reach Instagram's Graph API servers"""
    try:
        response = requests.get("https://graph.facebook.com/v23.0/", timeout=10)
        print(f"✅ Instagram Graph API reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Instagram Graph API: {e}")
    return False

def test_twitter_api_reach():
    """Test if we can reach Twitter's API servers"""
    try:
        response = requests.get("https://api.twitter.com/2/tweets/sample/stream", timeout=10)
        print(f"✅ Twitter API reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Twitter API: {e}")
    return False

def test_facebook_credentials():
    """Test Facebook credentials"""
    try:
        poster = fb_script.FacebookPoster()
        print("✅ Facebook credentials found in .env")
        
        if poster.verify_token():
            if poster.verify_page_access():
                print("✅ Facebook page access verified")
                return True
            else:
                print("❌ Facebook page access failed")
        else:
            print("❌ Facebook token verification failed")
    except ValueError as e:
        print(f"❌ Facebook credentials missing: {e}")
    except Exception as e:
        print(f"❌ Facebook authentication failed: {e}")
    
    return False

def test_instagram_credentials():
    """Test Instagram credentials"""
    try:
        poster = instagram_script.InstagramPoster()
        print("✅ Instagram credentials found in .env")
        
        account_info = poster.get_account_info()
        if account_info:
            username = account_info.get('username', 'unknown')
            print(f"✅ Instagram account verified: @{username}")
            return True
        else:
            print("❌ Instagram account verification failed")
    except ValueError as e:
        print(f"❌ Instagram credentials missing: {e}")
    except Exception as e:
        print(f"❌ Instagram authentication failed: {e}")
    
    return False

def test_twitter_credentials():
    """Test Twitter credentials with minimal setup"""
    API_KEY = os.getenv("TWITTER_API_KEY")
    API_SECRET = os.getenv("TWITTER_API_SECRET_KEY")
    ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET_TOKEN")
    
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        print("❌ Missing Twitter credentials in .env file")
        return False
    
    print("✅ All Twitter credentials found in .env")
    
    try:
        # Try with correct configuration (no timeout parameter)
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        # Simple API call without invalid timeout parameter
        me = client.get_me()
        if me.data:
            print(f"✅ Twitter API authentication successful: @{me.data.username}")
            return True
            
    except Exception as e:
        print(f"❌ Twitter authentication failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🔍 Multi-Platform Social Media Diagnostic Tool")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    print("1. Testing internet connection...")
    internet_ok = test_internet_connection()
    
    # Test API reachability
    print("\n2. Testing API Reachability...")
    twitter_reach = test_twitter_api_reach()
    facebook_reach = test_facebook_api_reach()
    instagram_reach = test_instagram_api_reach()
    
    # Test credentials
    print("\n3. Testing Credentials...")
    twitter_creds = test_twitter_credentials()
    facebook_creds = test_facebook_credentials()
    instagram_creds = test_instagram_credentials()
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 50)
    print(f"Twitter: Reach {'✅' if twitter_reach else '❌'} | Creds {'✅' if twitter_creds else '❌'}")
    print(f"Facebook: Reach {'✅' if facebook_reach else '❌'} | Creds {'✅' if facebook_creds else '❌'}")
    print(f"Instagram: Reach {'✅' if instagram_reach else '❌'} | Creds {'✅' if instagram_creds else '❌'}")
    
    all_working = all([twitter_reach, twitter_creds, 
                      facebook_reach, facebook_creds,
                      instagram_reach, instagram_creds])
    
    if internet_ok and all_working:
        print("\n🎉 All platforms working perfectly!")
    else:
        print("\n⚠️  Some issues detected:")
        
        if not internet_ok:
            print("  🔧 Fix: Check your internet connection")
        if not twitter_reach:
            print("  🔧 Fix: Check firewall/proxy settings for Twitter")
        if not facebook_reach:
            print("  🔧 Fix: Check firewall/proxy settings for Facebook")
        if not instagram_reach:
            print("  🔧 Fix: Check firewall/proxy settings for Instagram")
        if not twitter_creds:
            print("  🔧 Fix: Verify Twitter API credentials")
        if not facebook_creds:
            print("  🔧 Fix: Verify Facebook API credentials")
        if not instagram_creds:
            print("  🔧 Fix: Verify Instagram API credentials")