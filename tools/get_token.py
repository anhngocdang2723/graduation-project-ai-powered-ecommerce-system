import requests
import sys

def login(email, password):
    url = "http://localhost:9000/auth/user/emailpass"
    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Full Response: {response.json()}")
            print(f"Token: {response.json().get('access_token')}")
            return response.json().get('access_token')
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    login("admin@dev.com", "admindev")
