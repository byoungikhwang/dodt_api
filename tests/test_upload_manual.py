from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
import os
import pytest # pytest 임포트 추가
import shutil # shutil 임포트 추가

# Mock user (fixture 사용을 위해 변경 가능)
def mock_get_current_user_sync(): # 동기 함수로 변경
    return {"sub": "1", "email": "test@example.com", "role": "MEMBER", "name": "Test User", "picture": "http://example.com/pic.jpg"}

@pytest.fixture(scope="module")
def test_client():
    # 테스트 전 UPLOAD_DIRECTORY 정리
    files_dir = "app/static/files"
    if os.path.exists(files_dir):
        shutil.rmtree(files_dir)
    os.makedirs(files_dir)

    with TestClient(app) as client:
        # 의존성 오버라이드
        app.dependency_overrides[get_current_user] = mock_get_current_user_sync
        yield client
        # 테스트 후 의존성 오버라이드 제거 및 파일 정리
        app.dependency_overrides.pop(get_current_user)
        # 테스트 데이터 파일 정리
        if os.path.exists(files_dir):
            shutil.rmtree(files_dir)

def test_upload_csv(test_client: TestClient): # fixture 사용
    # Create a dummy CSV file
    csv_content = "age,income,score\n25,50000,80\n30,60000,85\n35,70000,90\n40,80000,95\n22,45000,75\n28,55000,82\n45,90000,92\n50,100000,98"
    files = {"file": ("test_upload.csv", csv_content, "text/csv")}
    
    response = test_client.post("/api/analysis/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
    assert "personas" in data
    assert data["total_users"] == 8 # 더 많은 assert 추가 가능
    
    # 파일이 생성되었는지 확인 (클린업은 fixture에서 처리)
    files_dir = "app/static/files"
    uploaded_files = [f for f in os.listdir(files_dir) if "test_upload" in f]
    assert len(uploaded_files) > 0
