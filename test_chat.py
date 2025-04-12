import requests
import json
import time

def test_chat():
    # Test data
    url = "http://192.0.0.2:8000/chat"
    data = {
        "message": "Hello!",
        "uuid": "572A866E-F602-477C-95EC-BD9463107D4F"
    }
    
    print("="*50)
    print("SENDING CHAT REQUEST")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        # Send request with timeout
        start_time = time.time()
        response = requests.post(url, json=data, timeout=10)
        end_time = time.time()
        
        print(f"\nRequest took: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            print(f"Response body: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Raw response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 10 seconds")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error - Is the server running?")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("="*50)

if __name__ == "__main__":
    test_chat() 