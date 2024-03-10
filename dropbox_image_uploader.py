import dropbox
import requests
import os

APP_KEY = os.environ.get('DROPBOX_APP_KEY')
APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')
access_token = os.environ.get('DROPBOX_ACCESS_TOKEN')

# Function to refresh access token
def refresh_access_token(refresh_token):
    token_url = "https://api.dropbox.com/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(token_url, data=data, auth=(APP_KEY, APP_SECRET))
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Failed to refresh token")

def upload_image(dalle_url, filename):
    refresh_token = os.environ.get('DROPBOX_REFRESH_TOKEN')
    try:
        dbx = dropbox.Dropbox(os.environ.get('DROPBOX_ACCESS_TOKEN'))
        # Test if token is valid by making a simple API call
        dbx.users_get_current_account()
    except dropbox.exceptions.AuthError:
        # Refresh token if there's an authentication error
        access_token = refresh_access_token(refresh_token)
        dbx = dropbox.Dropbox(access_token)
    dropbox_path = '/'+filename
    print("Downloading image from URL...", dalle_url)
    response = requests.get(dalle_url)
    if response.status_code == 200:
        print("Uploading image to Dropbox...", dropbox_path)
        # Upload the image content directly from memory
        dbx.files_upload(response.content, dropbox_path)
        # Create a shared link with public settings
        settings = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
        link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path, settings=settings)
        # Get a direct link to the file
        direct_link = link_metadata.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace("?dl=0", "")
        print("Direct Link:", direct_link)
        return direct_link
    else:
        print("Failed to download image from URL")
        return None

upload_image('/home/lunkwill/projects/ComfyUI/output/The_Distress_Context_of_Social_Calls_Evokes_a_Fear_Response_in_the_Bat_Pipistrel_00006_.png')