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
#import dropbox_image_uploader
#import gdrive_image_uploader
import github_image_uploader
import my_google_secret
import json

#To update the code on the cloud
#gcloud functions deploy lemmy_auto_icon   --runtime python310   --trigger-http   --allow-unauthenticated   --entry-point=lemmy_auto_icon


#print(os.environ.get('OPENAI_API_KEY'))

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
    posts_data = lemmy_instance.post.list(community_id=community_id, sort='Hot', page=1, limit=5)

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
                {"role": "user", "content": "Create an witty, comedic, and playfully disrespectful/offesive AI Art prompt that will be to be used to make a single image based on an article title. The image will have two uses, it will be used as a small icon and the middle section of it will be used as a website banner. Remember that this will be used as a small icon, so it should be relatively simple and identifiable even at a very small size. It is absolutely crucial that the image be a slight mockery of the following article title, and should come from a place of playful ridicule. Here is the article title: "+post_title+"\nRespond with only the clever and thoughtful prompt that you are submitting. PROMPT: "}
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
    #response = requests.put('https://lemmy.world/api/v3/community', json=data)

    headers = {
        'User-Agent': 'Your User Agent String',
        #'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',  # Specify content type as JSON
    }

    # Make the PUT request
    response = requests.put('https://lemmy.world/api/v3/community', json=data, headers=headers)

    # Check response
    if response.status_code == 200:
        print(f"{icon_or_banner} updated successfully!")
    else:
        print(f"Failed to update {icon_or_banner}.")

update_lemmy_art("icon", 'https://drive.google.com/uc?export=view&id=1anSZHi14bBy3_CLD6MsbOweVnA4ycPO3')

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
    #response = requests.post("https://lemmy.world/api/v3/comment", json=payload, headers=headers)

    headers = {
        'User-Agent': 'Your User Agent String',
        #'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',  # Specify content type as JSON
    }

    # Make the POST request
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

# def set_image_as_icon(image_url, filename):
#     image_url_dropbox = dropbox_image_uploader.upload_image(image_url, filename)
#     print("image_url_dropbox", image_url_dropbox)
#     update_lemmy_art("icon", image_url_dropbox)
#     update_lemmy_art("banner", image_url_dropbox)
#     print("icon updated successfully!")
#     return image_url_dropbox

def set_image_as_icon(image_url, filename):
    image_url_gdrive = github_image_uploader.upload_image(image_url, filename)
    print("image_url_gdrive", image_url_gdrive)
    update_lemmy_art("icon", image_url_gdrive)
    update_lemmy_art("banner", image_url_gdrive)
    print("icon updated successfully!")
    return image_url_gdrive


async def send_telegram_alert(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

def read_gdrive_file(file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read().decode('utf-8')

def write_gdrive_file(file_id, content):
    fh = io.BytesIO(content.encode('utf-8'))
    media = MediaIoBaseUpload(fh, mimetype='text/plain')
    service.files().update(fileId=file_id, media_body=media).execute()

def get_unread_message_count_lemmy():
    auth_token = get_auth_token()    
    #response = requests.get(f"https://lemmy.world/api/v3/user/unread_count?auth={auth_token}")
    headers = {
        'User-Agent': 'Your User Agent String',
        #'Accept-Encoding': 'gzip, deflate, br',  # Sample additional header
        'Authorization': f'Bearer {auth_token}',  # Assuming Bearer token auth
    }
    response = requests.get("https://lemmy.world/api/v3/user/unread_count", headers=headers)
    total_count = 0
    print(response)
    print(response.text)
    
    if response.status_code == 200:
        response_json = json.loads(response.text)
        total_count = response_json["replies"] + response_json["mentions"] + response_json["private_messages"]
        print(f"there are {total_count} notifications")
    else:
        print(f"Failed to comment.")
    return total_count

async def check_and_update_top_post_async():
    # Attempt to download the current top post title from Google Drive
    current_post_title_file_id = '1dpzV4S9R-Fh1kKKJd51Pp0UlfZzAocIb'
    current_top_post = read_gdrive_file(current_post_title_file_id)
    latest_top_post_id, latest_top_post = get_highest_post(community_id)
    print('latest_top_post:', latest_top_post)
    if current_top_post != latest_top_post:
        print("Top post has changed. Updating Google Drive and executing response.")
        funny_image_prompt = generate_funny_image_prompt(latest_top_post)
        print('funny_image_prompt:', funny_image_prompt)
        image_url, filename = generate_image(funny_image_prompt)        
        dropbox_url = set_image_as_icon(image_url, filename)
        MESSAGE = 'The Lemmy image has been updated!'
        await send_telegram_alert(MESSAGE)
        print("New images set.")
        write_gdrive_file(current_post_title_file_id, latest_top_post)
        documenting_file_id = '10iqfoB0jHEhb8S3a_21mSkBxx6VfTP_v'
        documenting_content = read_gdrive_file(documenting_file_id)
        documenting_json = json.loads(documenting_content)
        documenting_json[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = {"post_title": latest_top_post, "image_url": dropbox_url}
        documenting_content = json.dumps(documenting_json)
        documentation_post_id = 7637523
        comment = f'''[{latest_top_post}](https://lemmy.world/post/{latest_top_post_id})

![]({dropbox_url})'''
        comment_on_lemmy_post(comment, documentation_post_id)

        write_gdrive_file(documenting_file_id, documenting_content)

    #check for new unread messages
    unread_count_file_id = "1zuLGt8A0GTWnBn-omeA_ki_XXSgMVgdU"
    unread_message_count_from_file = read_gdrive_file(unread_count_file_id)
    unread_message_count_from_lemmy = get_unread_message_count_lemmy()
    print('unread_message_count_from_file:', unread_message_count_from_file)
    print('unread_message_count_from_lemmy:', unread_message_count_from_lemmy)
    if int(unread_message_count_from_file) < int(unread_message_count_from_lemmy):
        write_gdrive_file(unread_count_file_id, str(unread_message_count_from_lemmy))
        MESSAGE = f'You have {unread_message_count_from_lemmy} Lemmy notifications!'
        await send_telegram_alert(MESSAGE)
    if int(unread_message_count_from_file) > int(unread_message_count_from_lemmy):
        write_gdrive_file(unread_count_file_id, str(unread_message_count_from_lemmy))

async def main(request=None):    
    await check_and_update_top_post_async()

def lemmy_auto_icon(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(main(request))
    loop.close()
    return jsonify({'message': 'Function executed successfully'}), 200

# #print(lemmy_auto_icon("request"))
#lemmy_auto_icon("request")

# auth_token = get_auth_token()    
# response = requests.get(f"https://lemmy.world/api/v3/user/unread_count?auth={auth_token}")
# total_count = 0
# print(response)
# print(response.text)

# https://lemmy.world/api/v3/user/unread_count?auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDc1MzIiLCJpc3MiOiJsZW1teS53b3JsZCIsImlhdCI6MTcwOTU3MTY1M30.NL9QXezDrW7xT4T42GrGPwvkO1cvB-VYR2bNCCqfgKs

# import requests

# auth_token = get_auth_token()
# headers = {
#     'User-Agent': 'Your User Agent String',
#     #'Accept-Encoding': 'gzip, deflate, br',  # Sample additional header
#     'Authorization': f'Bearer {auth_token}',  # Assuming Bearer token auth
# }
# response = requests.get("https://lemmy.world/api/v3/user/unread_count", headers=headers)

# print(response)
# print(response.text)
