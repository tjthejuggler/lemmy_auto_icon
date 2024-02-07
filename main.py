import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from lemmy import Lemmy
from openai import OpenAI
from telegram import Bot
import asyncio
import requests
from get_auth import get_auth_token
from datetime import datetime
import os
from flask import jsonify
import dropbox_image_uploader
import my_google_secret


print(os.environ.get('OPENAI_API_KEY'))

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

my_secret_content = my_google_secret.get_secret()

community_id = 78581

# Authenticate and create the service
creds = service_account.Credentials.from_service_account_info(
    my_secret_content, scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

def get_highest_post(community_id, excluded_title="Bioacoustics Resources"):
    lemmy_instance = Lemmy("https://lemmy.world")

    # Fetch the hottest posts from the community
    posts_data = lemmy_instance.post.list(community_id=community_id, sort='Active', page=1, limit=5)

    if 'posts' in posts_data:
        # Skip the first post and get the second post
        for i, post_data in enumerate(posts_data['posts']):
            if i == 1:
                post = post_data['post']
                if post['name'] != excluded_title:
                    return post['id'], post['name']  # Return the ID and title of the second hottest post
    else:
        print("Failed to fetch posts or no posts available.")

    return None, None

def generate_funny_image_prompt(post_title):
    # Ensure your OpenAI API key is set before calling this function
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Ensure this is the correct engine name at your time of use
            #model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "You are an AI Art prompt creator."},
                {"role": "user", "content": "From the top of your intelligence, create an AI Art prompt to be used as a small clever and humorous icon to represent the following article. Respond with only the prompt. Here is the title of the article: "+post_title+"\nPrompt: "}
            ],
            max_tokens=60
        )
        print(response)
        # Assuming `completion` is your ChatCompletion object:
        completion_content = response.choices[0].message.content.strip()
        print(completion_content)
        # Extract and return the generated text
        return completion_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print('response', response)
    # Check if the response has data and a URL for the image
    if response.data and response.data[0].url:
        image_url = response.data[0].url
        # Download the image from the URL
        image_response = requests.get(image_url)
        #get todays date and time to make a unique filename
        date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = 'lemmy_auto_icon' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.png'
        # Save the image to a file
        if image_response.status_code == 200:
            # with open(filename, 'wb') as image_file:
            #     image_file.write(image_response.content)
            print("Image saved successfully.")
            return(image_url, filename)
        else:
            print("Failed to download the image.")
    else:
        print("No image URL found in the response.")

def update_lemmy_art(icon_or_banner, icon_url):
    auth_token = get_auth_token()
    if icon_or_banner == "icon":
        # Data to be sent
        data = {
            'community_id': 78581,
            'icon': icon_url,  # Change this to the appropriate key for the icon
            'auth': auth_token  # Include the auth token in the request body
        }
    else:
        # Data to be sent
        data = {
            'community_id': 78581,
            'banner': icon_url,  # Change this to the appropriate key for the icon
            'auth': auth_token  # Include the auth token in the request body
        }
    # Making the PUT request
    response = requests.put('https://lemmy.world/api/v3/community', json=data)
    # Check response
    if response.status_code == 200:
        print(f"{icon_or_banner} updated successfully!")
    else:
        print(f"Failed to update {icon_or_banner}.")

def set_image_as_icon(image_url, filename):
    image_url_dropbox = dropbox_image_uploader.upload_image(image_url, filename)
    print("image_url_dropbox", image_url_dropbox)
    update_lemmy_art("icon", image_url_dropbox)
    update_lemmy_art("banner", image_url_dropbox)
    print("icon updated successfully!")

async def send_telegram_alert(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

async def check_and_update_top_post_async():
    # Attempt to download the current top post title from Google Drive
    current_post_title_file_id = '1dpzV4S9R-Fh1kKKJd51Pp0UlfZzAocIb'
    request = service.files().get_media(fileId=current_post_title_file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    current_top_post = fh.read().decode('utf-8')    
    latest_top_post = get_highest_post(community_id)[1]
    print('latest_top_post:', latest_top_post)
    if current_top_post != latest_top_post:
        print("Top post has changed. Updating Google Drive and executing response.")
        funny_image_prompt = generate_funny_image_prompt(latest_top_post)
        print('funny_image_prompt:', funny_image_prompt)
        image_url, filename = generate_image(funny_image_prompt)        
        set_image_as_icon(image_url, filename)
        MESSAGE = 'The Lemmy image has been updated!'
        await send_telegram_alert(MESSAGE)
        print("New images set.")
        fh = io.BytesIO(latest_top_post.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='text/plain')
        service.files().update(fileId=current_post_title_file_id, media_body=media).execute()

async def main(request=None):    
    await check_and_update_top_post_async()

def lemmy_auto_icon(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(request))
    loop.close()
    return jsonify({'message': 'Function executed successfully'}), 200


# def lemmy_auto_icon(request):
#     asyncio.run(main(request))
#     # Return a simple JSON response indicating success or failure
#     return jsonify({'message': 'Function executed successfully'}), 200

# if __name__ == "__main__":
#     # Simulate an event loop for local testing
#     asyncio.run(main("Simulated request"))
#lemmy_auto_icon("request")
#asyncio.run(bot_interaction())