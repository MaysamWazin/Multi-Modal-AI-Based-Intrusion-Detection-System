# test_client.py
import requests

url = "http://127.0.0.1:8000/predict"

# 8 boyutlu dummy feature (sadece deneme için)
dummy_features = [10, 20, 443, 51515, 6, 0.0, 500.0, 1.0]

payload = {
    "features": dummy_features
}

try:
    res = requests.post(url, json=payload)
    print("Status code:", res.status_code)
    print("Response JSON:", res.json())
except Exception as e:

    print("Hata oluştu:", e)
    