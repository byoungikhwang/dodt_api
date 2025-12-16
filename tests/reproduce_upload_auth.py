import os
import sys
from app.auth.jwt_handler import create_access_token
from fastapi.testclient import TestClient
from app.main import app # app 임포트 추가

# Add project root to sys.path
sys.path.append(os.getcwd())

def test_upload_with_cookie(): # async 제거
    # 1. Create a valid token
    token = create_access_token({"sub": "test_user", "email": "test@example.com"})
    
    # 2. Prepare a dummy CSV file
    files = {'file': ('test.csv', 'col1,col2\nval1,val2', 'text/csv')}
    
    # 3. Make request with cookie
    client = TestClient(app) # TestClient 인스턴스화
    
    # Set cookie
    client.cookies.set("access_token", f"Bearer {token}")
    
    # Upload
    response = client.post("/api/analysis/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("SUCCESS: Upload accepted with cookie auth.")
    elif response.status_code == 401:
        print("FAILURE: Still 401 Unauthorized.")
    else:
        print(f"FAILURE: Unexpected status code {response.status_code}")

if __name__ == "__main__":
    test_upload_with_cookie()