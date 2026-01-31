from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_prediction_fonctionne():
    # 1. Login
    login_response = client.post(
        "/token", 
        data={"username": "admin", "password": "admin123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    
    # 2. Predict
    test_data  ={
        "trip_distance": 20.0,
        "pickup_hour": 10,
        "day_of_week": 6,
        "month": 4
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    reponse = client.post("/predict", json=test_data, headers=headers)
    
    assert reponse.status_code == 200, f"Predict failed: {reponse.text}"
    
    resultat = reponse.json()
    assert "estimated_duration" in resultat
    assert resultat["estimated_duration"] > 0