from PIL import Image, PngImagePlugin
import requests
import base64
from dotenv import load_dotenv
import os
from datetime import datetime
import yaml

load_dotenv()
IMAGE_GENERATION_URL = os.getenv("SD_API_URL")
CACHE_DIR = "cache"
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def upload_to_imgbb(image_path, file_name):
    """
    Uploads image file to ImgBB and returns the URL.
    Args:
        image_path (str): Path to the image file.
        file_name (str): Name of the image file.
    Returns:
        str: URL of the uploaded image on ImgBB.
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={
                "key": IMGBB_API_KEY,
            },
            files={
                "image": (file_name, image_data)
            }
        )
        response.raise_for_status()
        result = response.json()
        if result["data"] and "url" in result["data"]:
            return result["data"]["url"]
        else:
            print("Failed to upload image to ImgBB.")
            return None
    except requests.RequestException as e:
        print(f"Error uploading image to ImgBB: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error uploading image to ImgBB: {e}")
        return None

def generate_sd(prompt):
    """
    Generate an image using the specified prompt and save it to the cache directory.
    Embeds the YAML payload into the image metadata.
    Returns:
        image_data (bytes): Raw image data as bytes.
        image_path (str): Absolute path to the saved image file using forward slashes.
        image_url (str): URL of the uploaded image on ImgBB.
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
            image_filename = f"image_{timestamp}.png"
            image_path = os.path.abspath(os.path.join(CACHE_DIR, image_filename))

            # Save the image as a PNG file
            with open(image_path, 'wb') as f:
                f.write(image_data)

            # Open the image with Pillow
            img = Image.open(image_path)

            # Convert payload to YAML string
            yaml_data = yaml.dump(payload)

            # Embed YAML data into image metadata
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("YAML", yaml_data)

            # Save the image with updated metadata
            img.save(image_path, "PNG", pnginfo=metadata)

            # Upload image to ImgBB
            image_url = upload_to_imgbb(image_path, image_filename)

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

if __name__ == "__main__":
    prompt = "your_prompt_here"  # Replace with your prompt
    image_data, image_path, image_url = generate_sd(prompt)
    if image_data and image_path and image_url:
        print(f"Image saved at: {image_path}")
        print(f"Image URL: {image_url}")
    else:
        print("Failed to generate or upload image.")
