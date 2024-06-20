import requests
import base64
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
IMAGE_GENERATION_URL = os.getenv("SD_API_URL")
CACHE_DIR = "cache"

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_sd(prompt):
    """
    Generate an image using the specified prompt and save it to the cache directory.

    Returns:
        image_data (bytes): Raw image data as bytes.
        image_path (str): Absolute path to the saved image file using forward slashes.
    """
    # Define payload for the POST request
    payload = {
        "prompt": prompt,
        "steps": 30,
        "width": "1024",
        "height": "1024",
        "negative_prompt": "lowres, bad body parts, bad anatomy, bad hands, bad face, bad eyes, bad mouth, bad ears, bad legs, ugly face, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, cartoon, anime, unrealistic, noise, blurry, 2d, 3d, illustrate, oil paint, render",
    }

    try:
        # Send POST request to the image generation endpoint
        response = requests.post(url=IMAGE_GENERATION_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        r = response.json()

        # Decode the image and save it to the cache folder
        if 'images' in r and r['images']:
            image_data = base64.b64decode(r['images'][0])
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filename = f"image_{timestamp}.png"
            image_path = os.path.abspath(os.path.join(CACHE_DIR, image_filename))

            with open(image_path, 'wb') as f:
                f.write(image_data)

            # Convert the path to use forward slashes
            image_path = image_path.replace('\\', '/')

            return image_data, image_path
        else:
            print("No images found in the response.")
            return None, None
    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
        return None, None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None, None
