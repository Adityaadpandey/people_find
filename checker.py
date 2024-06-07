import json
import face_recognition
import numpy as np

# Load the JSON data with embeddings
with open('instagram_followings/followings_data.json', 'r') as f:
    followings_data = json.load(f)

# Function to calculate Euclidean distance between two face embeddings
def calculate_distance(embedding1, embedding2):
    return np.linalg.norm(np.array(embedding1) - np.array(embedding2))

# Function to find the closest match
def find_closest_match(image_path, followings_data):
    # Load the input image and calculate its face embedding
    input_image = face_recognition.load_image_file(image_path)
    input_embedding = face_recognition.face_encodings(input_image)
    
    if not input_embedding:
        print("No face found in the input image.")
        return None
    
    input_embedding = input_embedding[0]

    # Initialize variables to track the closest match
    closest_match = None
    closest_distance = float('inf')

    # Iterate through followings' embeddings to find the closest match
    for following in followings_data:
        if following['face_embedding'] is not None:
            distance = calculate_distance(input_embedding, following['face_embedding'])
            if distance < closest_distance:
                closest_distance = distance
                closest_match = following

    return closest_match

# Main function to take an input image and find the closest match
def main(image_path):
    closest_match = find_closest_match(image_path, followings_data)
    if closest_match:
        print(f"Closest match: {closest_match['username']} - {closest_match['full_name']}")
    else:
        print("No match found.")

# Example usage
if __name__ == '__main__':
    input_image_path = 'test.jpg'
    main(input_image_path)
