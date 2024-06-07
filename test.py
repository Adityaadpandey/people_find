import instaloader
import os
import json
import requests
from datetime import datetime
import face_recognition
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Instaloader
L = instaloader.Instaloader()

# Function to download profile picture
def download_profile_pic(path, url):
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Download the picture
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as out_file:
                for chunk in response.iter_content(1024):
                    out_file.write(chunk)
            os.utime(path, (datetime.now().timestamp(), datetime.now().timestamp()))
            print(f"Downloaded: {path}")
        else:
            print(f"Failed to download {url}: {response.status_code}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Function to check if an image contains a face and generate embeddings
def get_face_embedding(image_path):
    try:
        # Load the image file into a numpy array
        image = face_recognition.load_image_file(image_path)
        # Find all the faces and face encodings in the image
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0]  # Return the first face encoding found
        else:
            return None
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")
        return None

# Get Instagram username and password from environment variables
instagram_username = os.getenv("INSTAGRAM_USERNAME")
instagram_password = os.getenv("INSTAGRAM_PASSWORD")

# Check if Instagram username and password are provided
if not instagram_username or not instagram_password:
    raise ValueError("Instagram username or password not found in environment variables.")

# Try to load session cookies
try:
    L.load_session_from_file(instagram_username)
except FileNotFoundError:
    # If session file doesn't exist, log in and save session
    L.login(instagram_username, instagram_password)
    L.save_session_to_file()

# Load profile of your account
profile = instaloader.Profile.from_username(L.context, instagram_username)

# Create a directory to save the data
directory = 'instagram_followings'
if not os.path.exists(directory):
    os.makedirs(directory)

# Fetch and save data of followings
followings_data = []
for following in profile.get_followees():
    username = following.username
    full_name = following.full_name
    profile_pic_url = following.profile_pic_url

    # Download profile picture
    profile_pic_path = f"{directory}/{username}.jpg"
    download_profile_pic(profile_pic_path, profile_pic_url)

    # Check if the profile picture contains a face and get the embedding
    face_embedding = get_face_embedding(profile_pic_path)
    
    # Append to followings data list
    followings_data.append({
        'username': username,
        'full_name': full_name,
        'profile_pic_path': profile_pic_path,
        'face_embedding': face_embedding.tolist() if face_embedding is not None else None
    })

    # Fetch and save data of followings' followings
    following_profile = instaloader.Profile.from_username(L.context, username)
    for ff in following_profile.get_followees():
        ff_username = ff.username
        ff_full_name = ff.full_name
        ff_profile_pic_url = ff.profile_pic_url

        # Download profile picture
        ff_profile_pic_path = f"{directory}/{ff_username}.jpg"
        download_profile_pic(ff_profile_pic_path, ff_profile_pic_url)

        # Check if the profile picture contains a face and get the embedding
        ff_face_embedding = get_face_embedding(ff_profile_pic_path)

        # Append to followings data list
        followings_data.append({
            'username': ff_username,
            'full_name': ff_full_name,
            'profile_pic_path': ff_profile_pic_path,
            'face_embedding': ff_face_embedding.tolist() if ff_face_embedding is not None else None
        })

# Save followings data to a JSON file
with open(f'{directory}/followings_data.json', 'w') as f:
    json.dump(followings_data, f, indent=4)

print("Data fetched and saved successfully.")