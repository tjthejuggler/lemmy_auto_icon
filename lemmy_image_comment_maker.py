import requests
from get_auth import get_auth_token
from lemmy import Lemmy


def comment_on_lemmy_post(comment, post_id):
    auth_token = get_auth_token()
    payload = {
        "content": comment,
        "post_id": post_id,
        'auth': auth_token,
        "parent_id": 0,
        "language_id": 0
    }    
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post("https://lemmy.world/api/v3/comment", json=payload, headers=headers)

    # Making the PUT request
    #response = requests.put('https://lemmy.world/api/v3/community', json=data)
    # Check response
    print(response)
    print(response.text)
    if response.status_code == 200:
        print(f"comment made successfully!")
    else:
        print(f"Failed to comment.")
while True:
    # Ask for the number, title, and URL from the user
    number = input("Enter the number: ")
    title = input("Enter the title: ")
    image_url = input("Enter the image URL: ")

    # Format the URL to be embedded in Markdown
    formatted_image_url = image_url.replace("https://www.dropbox.com", "https://dl.dropboxusercontent.com").replace("?dl=0", "&dl=0")

    # Create the Markdown formatted text
    markdown_text = f"[{title}](https://lemmy.world/post/{number})\n\n![]({formatted_image_url})"

    # Print the resulting text to be copied
    print("\nCopy the following Markdown text:\n")
    print(markdown_text)



    documentation_post_id = 7637523
    comment_on_lemmy_post(markdown_text, documentation_post_id)