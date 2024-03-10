from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import requests
import tempfile
import os
import my_google_secret  # Ensure this module correctly fetches your service account info

def build_service():
    # Load the service account credentials from your secret storage
    my_secret_content = my_google_secret.get_secret()
    creds = service_account.Credentials.from_service_account_info(
        my_secret_content, scopes=['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=creds)

def upload_image(image_url, filename):
    service = build_service()
    response = requests.get(image_url)
    if response.status_code == 200:
        # Temporarily save the image file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Prepare the file metadata and upload media
        file_metadata = {'name': filename}
        media = MediaFileUpload(temp_file_path, mimetype='image/png', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        os.remove(temp_file_path)  # Clean up the temporary file
        
        file_id = file.get('id')
        
        # Make the file publicly accessible
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file_id, body=permission).execute()
        
        # Construct and return the shareable link
        file_link = f"https://drive.google.com/uc?id={file_id}"
        print("File Link:", file_link)
        return file_link
    else:
        print("Failed to download image from URL")
        return None
