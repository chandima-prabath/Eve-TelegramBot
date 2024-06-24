from PIL import Image
import yaml

def read_payload_from_image(image_path):
    """
    Reads and extracts the YAML payload embedded in the PNG image metadata.
    
    Args:
        image_path (str): Path to the PNG image file.
        
    Returns:
        dict or None: Extracted YAML payload as a dictionary if found, None otherwise.
    """
    try:
        # Open the image with Pillow
        img = Image.open(image_path)
        
        # Check if the image is a PNG and has metadata
        if img.format == "PNG" and isinstance(img.info, dict) and "YAML" in img.info:
            yaml_data = img.info["YAML"]
            
            # Convert YAML string to dictionary
            payload = yaml.safe_load(yaml_data)
            return payload
        else:
            print("No YAML payload found in the PNG image metadata.")
            return None
    except Exception as e:
        print(f"Error reading payload from image: {e}")
        return None

# Example usage if executed directly (not necessary in the module version)
if __name__ == "__main__":
    image_path = "cache/image_20240624111031.png"  # Replace with the actual path to your PNG image file
    payload = read_payload_from_image(image_path)
    if payload:
        print("Extracted YAML payload:")
        print(yaml.dump(payload, default_flow_style=False))
    else:
        print("Failed to extract YAML payload.")
