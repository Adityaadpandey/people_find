import instaloader
import os
import json
import requests
from datetime import datetime
import face_recognition
from dotenv import load_dotenv
from multiprocessing import Pool, cpu_count

# Load environment variables from .env file
load_dotenv()

# Initialize Instaloader
L = instaloader.Instaloader()

# Function to download profile picture
def download_profile_pic(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        profile_pic_url = profile.profile_pic_url
        profile_pic_path = f"instagram_followings/{username}.jpg"
        response = requests.get(profile_pic_url, stream=True)
        if response.status_code == 200:
            with open(profile_pic_path, 'wb') as out_file:
                out_file.write(response.content)
            os.utime(profile_pic_path, (datetime.now().timestamp(), datetime.now().timestamp()))
            return username, profile_pic_path
        else:
            print(f"Failed to download {profile_pic_url}: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Failed to download profile picture for {username}: {e}")
        return None, None

# Function to check if an image contains a face and generate embeddings
def get_face_embedding(profile_pic_path):
    try:
        image = face_recognition.load_image_file(profile_pic_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            return face_encodings[0].tolist()
        else:
            return None
    except Exception as e:
        print(f"Failed to process {profile_pic_path}: {e}")
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
    L.login(instagram_username, instagram_password)
    L.save_session_to_file()

# Load profile of your account
profile = instaloader.Profile.from_username(L.context, instagram_username)

# Create a directory to save the data
directory = 'instagram_followings'
if not os.path.exists(directory):
    os.makedirs(directory)

# Function to process each user
def process_user(username):
    profile_pic_username, profile_pic_path = download_profile_pic(username)
    if profile_pic_username and profile_pic_path:
        face_embedding = get_face_embedding(profile_pic_path)
        return {
            'username': profile_pic_username,
            'profile_pic_path': profile_pic_path,
            'face_embedding': face_embedding
        }
    else:
        return None

# Fetch and save data of followings
followings_data = []
followings = [following.username for following in profile.get_followees()]

# Parallel processing for followings
with Pool(cpu_count()) as pool:
    followings_data = pool.map(process_user, followings)

# Filter out None results
followings_data = [data for data in followings_data if data is not None]

# Fetch and save data of followings' followings
for following in followings:
    try:
        following_profile = instaloader.Profile.from_username(L.context, following)
        followings_followings = [ff.username for ff in following_profile.get_followees()]

        with Pool(cpu_count()) as pool:
            followings_followings_data = pool.map(process_user, followings_followings)

        followings_followings_data = [data for data in followings_followings_data if data is not None]
        followings_data.extend(followings_followings_data)
    except Exception as e:
        print(f"Failed to fetch followings for {following}: {e}")

# Save followings data to a JSON file
with open(f'{directory}/followings_data.json', 'w') as f:
    json.dump(followings_data, f, indent=4)

print("Data fetched and saved successfully.")
