import json
import face_recognition
import numpy as np

# Load the JSON data with embeddings
with open('followings_data.json', 'r') as f:
    followings_data = json.load(f)

# Function to calculate Euclidean distance between two face embeddings
def calculate_distance(embedding1, embedding2):
    return np.linalg.norm(np.array(embedding1) - np.array(embedding2))

# Function to find all matches sorted by their distance
def find_all_matches(image_path, followings_data):
    # Load the input image and calculate its face embedding
    input_image = face_recognition.load_image_file(image_path)
    input_embedding = face_recognition.face_encodings(input_image)
    
    if not input_embedding:
        print("No face found in the input image.")
        return []

    input_embedding = input_embedding[0]

    # Initialize a list to store matches and their distances
    matches = []

    # Iterate through followings' embeddings to find all matches
    for following in followings_data:
        if following['face_embedding'] is not None:
            distance = calculate_distance(input_embedding, following['face_embedding'])
            matches.append((following, distance))

    # Sort the matches by distance
    matches.sort(key=lambda x: x[1])

    return matches

# Main function to take an input image and find the top N closest matches
def main(image_path, top_n=5, max_distance=0.6):
    all_matches = find_all_matches(image_path, followings_data)
    if all_matches:
        closest_matches = [match for match in all_matches if match[1] <= max_distance][:top_n]
        if closest_matches:
            print(f"Top {top_n} closest matches within distance {max_distance}:")
            for match, distance in closest_matches:
                print(f"Username: {match['username']}, Distance: {distance}")
        else:
            print(f"No matches found within the distance of {max_distance}.")
    else:
        print("No matches found.")

# Example usage
if __name__ == '__main__':
    input_image_path = 'testt.jpeg'
    main(input_image_path, top_n=8, max_distance=0.6)
