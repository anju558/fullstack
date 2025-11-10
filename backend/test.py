# test_api.py
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    print("🔹 Testing /signup...")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Passw0rd!",
        "confirm_password": "Passw0rd!"
    }
    res = requests.post(f"{BASE_URL}/signup", data=data)
    print("Status:", res.status_code)
    print("Response:", res.json())
    assert res.status_code == 200
    user_id = res.json()["user_id"]
    print("✅ Signup success. User ID:", user_id)
    return user_id

def test_login():
    print("\n🔹 Testing /login...")
    data = {
        "email": "test@example.com",
        "password": "Passw0rd!"
    }
    res = requests.post(f"{BASE_URL}/login", data=data)
    print("Status:", res.status_code)
    print("Response:", res.json())
    assert res.status_code == 200
    user_id = res.json()["user_id"]
    print("✅ Login success. User ID:", user_id)
    return user_id

def test_create_shipment():
    print("\n🔹 Testing /shipments POST...")
    shipment_data = {
        "Shipment_Number": "SHIP12345",
        "Route_Details": "Delhi to Mumbai",
        "Device": "GPS-001",
        "Po_Number": "PO98765",
        "NDC_Number": "NDC54321",
        "Serial_Number_of_Goods": "SN112233",
        "Container_number": "CONT-789",
        "Goods_Type": "Electronics",
        "Expected_Delivery_Date": "2025-12-01",
        "delivery_number": "DEL-456",
        "Batch_ID": "BATCH-789",
        "Shipment_Description": "Laptops batch #A1"
    }
    res = requests.post(f"{BASE_URL}/shipments", json=shipment_data)
    print("Status:", res.status_code)
    print("Response:", res.json())
    assert res.status_code == 200
    print("✅ Shipment created:", res.json()["Shipment_Number"])

if __name__ == "__main__":
    try:
        test_signup()
        time.sleep(0.5)
        test_login()
        time.sleep(0.5)
        test_create_shipment()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print("\n❌ Test failed:", e)