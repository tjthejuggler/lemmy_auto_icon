import requests
import os
import tempfile
import base64
# Replace these with your own details
GITHUB_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
REPO_NAME = 'tjthejuggler/lemmy_auto_icon'  # Format: 'username/repo'
BRANCH_NAME = 'main'  # Or your target branch
PATH = 'images/'  # Folder path in your repo, make sure it exists or is empty string if not needed

def upload_image(image_url, filename):
    # Download the image from the given URL
    response = requests.get(image_url)
    if response.status_code == 200:
        # Temporarily save the image to disk
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.png') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Prepare for the GitHub API request
        api_url = f'https://api.github.com/repos/{REPO_NAME}/contents/{PATH}{filename}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
        }
        with open(temp_file_path, 'rb') as file:
            content = file.read()

        # Correctly encode the content to base64
        encoded_content = base64.b64encode(content).decode('utf-8')

        data = {
            'message': f'Add {filename}',
            'branch': BRANCH_NAME,
            'content': encoded_content,
        }
        
        # Make the request to GitHub API
        response = requests.put(api_url, headers=headers, json=data)
        os.remove(temp_file_path)  # Clean up the temporary file

        if response.status_code in [200, 201]:
            print("File uploaded successfully to GitHub.")
            # Construct and return the URL
            file_url = f'https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH_NAME}/{PATH}{filename}'
            print("File URL:", file_url)
            return file_url
        else:
            print("Failed to upload file to GitHub:", response.json())
            return None
    else:
        print("Failed to download image from URL")
        return None

# # Example usage
# image_url = 'https://www.openstenoproject.org/plover/images/plover_screenshot.png'
# filename = 'example_image.png'  # Ensure this has the correct file extension
# upload_image(image_url, filename)
