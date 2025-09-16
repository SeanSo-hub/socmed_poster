import requests
import tweepy
import os
from dotenv import load_dotenv

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

def test_twitter_api_reach():
    """Test if we can reach Twitter's API servers"""
    try:
        response = requests.get("https://api.twitter.com/2/tweets/sample/stream", timeout=10)
        print(f"✅ Twitter API reachable (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Cannot reach Twitter API: {e}")
    return False

def test_credentials_simple():
    """Test credentials with minimal setup"""
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

def test_posting():
    """Test actual tweet posting"""
    try:
        API_KEY = os.getenv("TWITTER_API_KEY")
        API_SECRET = os.getenv("TWITTER_API_SECRET_KEY")
        ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET_TOKEN")
        
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        
        # Try posting a test tweet
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        test_message = f"Test tweet from diagnostic script at {timestamp} 🔧"
        
        response = client.create_tweet(text=test_message)
        if response.data:
            print(f"✅ Test tweet posted successfully! ID: {response.data['id']}")
            return True
            
    except Exception as e:
        print(f"❌ Tweet posting failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🔍 Running Twitter API diagnostics...\n")
    
    print("1. Testing internet connection...")
    internet_ok = test_internet_connection()
    
    print("\n2. Testing Twitter API reachability...")
    api_ok = test_twitter_api_reach()
    
    print("\n3. Testing Twitter credentials...")
    creds_ok = test_credentials_simple()
    
    print("\n4. Testing tweet posting...")
    post_ok = test_credentials_simple() and test_posting()
    
    print("\n" + "="*50)
    if internet_ok and api_ok and creds_ok and post_ok:
        print("🎉 All tests passed! Twitter API should work.")
    else:
        print("💥 Some tests failed. See issues above.")
        
        if not internet_ok:
            print("🔧 Fix: Check your internet connection")
        if not api_ok:
            print("🔧 Fix: Check firewall/proxy settings")
        if not creds_ok:
            print("🔧 Fix: Verify Twitter API credentials")
        if not post_ok:
            print("🔧 Fix: Check posting permissions")