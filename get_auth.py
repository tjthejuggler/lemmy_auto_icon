import requests
import os

def get_auth_token():
    auth_token = "None"
    # Your Lemmy credentials
    username = os.environ.get('LEMMY_USERNAME')
    password = os.environ.get('LEMMY_PASSWORD')

    # #/home/lunkwill/projects/lemmy_auto_icon/secrets/username.txt
    # with open ('/home/lunkwill/projects/lemmy_auto_icon/secrets/username.txt', 'r') as file:
    #     username = file.read().replace('\n', '')
    
    # with open ('/home/lunkwill/projects/lemmy_auto_icon/secrets/password.txt', 'r') as file:
    #     password = file.read().replace('\n', '')

    print("Username:", username)
    print("Password:", password)
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

if __name__ == "__main__":
    get_auth_token()