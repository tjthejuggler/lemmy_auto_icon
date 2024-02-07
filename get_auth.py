import requests
import os

def get_auth_token():
    auth_token = "None"
    # Your Lemmy credentials
    username = os.environ.get('LEMMY_USERNAME')
    password = os.environ.get('LEMMY_PASSWORD')

    # Login data
    login_data = {
        'username_or_email': username,
        'password': password
    }

    # Login request
    response = requests.post('https://lemmy.world/api/v3/user/login', json=login_data)

    # Extracting the auth token
    if response.status_code == 200:
        auth_token = response.json().get('jwt')
        print("Auth Token:", auth_token)
    else:
        print("Failed to log in.")
    return auth_token