from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Union
import os
import threading
import yaml
from image_payload_reader import read_payload_from_image
from telegram import start_telegram_bot

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Model for response
class ImageFile(BaseModel):
    image: str
    yaml: Dict[str, Union[str, int, float]]

class ImageResponse(BaseModel):
    image_files: List[ImageFile]

# Function to start the Telegram bot in a separate thread
def start_telegram():
    start_telegram_bot()

# Start the Telegram bot in a separate thread when the application starts
threading.Thread(target=start_telegram).start()

# Function to fetch image files and corresponding YAML data from 'cache' directory
def fetch_image_files():
    files = os.listdir('cache')
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
    response_data = []

    for image_file in image_files:
        yaml_file = image_file.rsplit('.', 1)[0] + '.yaml'
        yaml_data = {}
        if yaml_file in files:
            with open(os.path.join('cache', yaml_file), 'r') as file:
                yaml_data = yaml.safe_load(file)
        response_data.append({
            'image': image_file,
            'yaml': yaml_data
        })
    
    return response_data

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    # Render the HTML template with fresh image data
    image_data = fetch_image_files()
    return templates.TemplateResponse("index.html", {"request": request, "image_data": image_data})

@app.get('/images', response_model=ImageResponse)
def get_images():
    # Fetch fresh image data
    image_data = fetch_image_files()
    return ImageResponse(image_files=image_data)

@app.get('/cache/{image_name}', response_class=JSONResponse)
def get_image(image_name: str):
    file_path = os.path.join('cache', image_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get('/statics/{image_name}', response_class=JSONResponse)
def get_static_image(image_name: str):
    file_path = os.path.join('statics', image_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get('/yaml/{image_name}', response_class=JSONResponse)
def get_embedded_yaml(image_name: str):
    file_path = os.path.join('cache', image_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    # Use the function to read YAML payload from image metadata
    yaml_payload = read_payload_from_image(file_path)
    if yaml_payload:
        return yaml_payload
    else:
        raise HTTPException(status_code=404, detail="No YAML payload found in the image metadata")
