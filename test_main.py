from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
test_user_id = None

def test_create_user():
    global test_user_id
    response = client.post("/users/", json={"name": "unitest", "email": "unitest@example.com", "password": "password"})
    assert response.status_code == 200
    assert response.json()["name"] == "unitest"
    assert response.json()["email"] == "unitest@example.com"
    test_user_id = response.json()["id"]

def test_get_user():
    global test_user_id
    assert test_user_id is not None
    response = client.get(f"/users/{test_user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_user_id

def test_update_user():
    global test_user_id
    assert test_user_id is not None
    response = client.put(f"/users/{test_user_id}", json={"name": "updated_test", "email": "updated_test@example.com", "password": "new_password"})
    assert response.status_code == 200
    assert response.json()["name"] == "updated_test"
    assert response.json()["email"] == "updated_test@example.com"

def test_delete_user():
    global test_user_id
    assert test_user_id is not None
    response = client.delete(f"/users/{test_user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"
