import requests
import base64
from dotenv import load_dotenv
import os
from datetime import datetime
import io
import yaml

load_dotenv()
IMAGE_GENERATION_URL = os.getenv("SD_API_URL")
CACHE_DIR = "cache"

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def generate_sd(prompt):
    """
    Generate an image using the specified prompt and save it to the cache directory.

    Returns:
        image_data (bytes): Raw image data as bytes.
        image_path (str): Absolute path to the saved image file using forward slashes.
    """
    config = load_config()
    config = config['config']
    # Define payload for the POST request
    payload = {
        "prompt": prompt,
        "steps": config['SD']['steps'],
        "width": config['SD']['width'],
        "height": config['SD']['height'],
        "sampler_name": config['SD']['sampler_name'],
        "seed": -1,
        "cfg_scale": config['SD']['cfg_scale'],
        "negative_prompt": config['SD']['negative_prompt'],
    }

    try:
        # Send POST request to the image generation endpoint
        response = requests.post(IMAGE_GENERATION_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        r = response.json()

        # Decode the image and save it to the cache folder
        if 'images' in r and r['images']:
            image_data = base64.b64decode(r['images'][0])
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filename = f"image_{timestamp}.jpg"
            prompt_filename = f"image_{timestamp}.yaml"
            image_path = os.path.abspath(os.path.join(CACHE_DIR, image_filename))
            prompt_path = os.path.abspath(os.path.join(CACHE_DIR, prompt_filename))

            # Save the prompt to a YAML file
            with open(prompt_path, 'w') as f:
                yaml.dump(payload, f)

            # Save the image as a JPEG file
            with open(image_path, 'wb') as f:
                image = io.BytesIO(image_data)
                f.write(image.getbuffer())

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
