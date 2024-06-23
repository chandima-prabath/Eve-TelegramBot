import os
import logging
import threading
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from llm import generate_llm
from sd import generate_sd

# Load environment variables
load_dotenv()
GREEN_API_URL = os.getenv("GREEN_API_URL")
GREEN_API_MEDIA_URL = os.getenv("GREEN_API_MEDIA_URL", "https://api.green-api.com")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
GREEN_API_ID_INSTANCE = os.getenv("GREEN_API_ID_INSTANCE")
WEBHOOK_AUTH_TOKEN = os.getenv("WEBHOOK_AUTH_TOKEN")
PORT = int(os.getenv("PORT"))

if not all([GREEN_API_URL, GREEN_API_TOKEN, GREEN_API_ID_INSTANCE, WEBHOOK_AUTH_TOKEN]):
    raise ValueError("Environment variables are not set properly")

# Configure logging
LOG_FILE = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def send_message(message_id, to_number, message, retries=3):
    """
    Send a text message using Green API with retry logic.
    """
    if to_number.endswith('@g.us'):
        chat_id = to_number
        is_group = True
    else:
        chat_id = to_number
        is_group = False

    url = f"{GREEN_API_URL}/waInstance{GREEN_API_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": chat_id,
        "message": message,
        "quotedMessageId": message_id,
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} - Failed to send message to {chat_id}: {e}")
            if attempt < retries - 1:
                continue
            return {"error": str(e)}

def send_image(message_id, to_number, image_path, retries=3):
    """
    Send an image using Green API with retry logic.
    """
    if to_number.endswith('@g.us'):
        chat_id = to_number
        is_group = True
    else:
        chat_id = to_number
        is_group = False

    url = f"{GREEN_API_MEDIA_URL}/waInstance{GREEN_API_ID_INSTANCE}/sendFileByUpload/{GREEN_API_TOKEN}"
    payload = {'chatId': chat_id, 'caption': 'Here you go!', 'quotedMessageId': message_id}
    files = [('file', ('image.jpg', open(image_path, 'rb'), 'image/jpeg'))]

    for attempt in range(retries):
        try:
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} - Failed to send image to {chat_id}: {e}")
            if attempt < retries - 1:
                continue
            return {"error": str(e)}

def response_text(message_id, chat_id, prompt):
    """
    Generate a response using the LLM and send it to the user.
    """
    try:
        msg = generate_llm(prompt)
        send_message(message_id, chat_id, msg)
        logger.info(f"Chat ID: {chat_id} - Sent Message: {msg}")
    except Exception as e:
        logger.error(f"Chat ID: {chat_id} - Error in response_text: {e}")
        send_message(message_id, chat_id, "There was an error processing your request.")

def handle_image_generation(message_id, chat_id, prompt):
    """
    Generate an image from the provided prompt and send it to the user.
    """
    try:
        image_data, image_path = generate_sd(prompt)
        logger.info(f"Image path {image_path}")
        if image_data:
            send_image(message_id, chat_id, image_path)
            logger.info(f"Chat ID: {chat_id} - Sent Image {image_path}")
        else:
            send_message(message_id, chat_id, "Failed to generate image. Please try again later.")
            logger.error(f"Chat ID: {chat_id} - Failed to generate image.")
    except Exception as e:
        logger.error(f"Chat ID: {chat_id} - Error in handle_image_generation: {e}")
        send_message(message_id, chat_id, "There was an error generating the image. Please try again later.")

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Handle incoming WhatsApp messages.
    """
    data = request.get_json()
    auth_header = request.headers.get('Authorization').strip()

    # logger.info(f"Received Authorization header: {auth_header}")
    # logger.info(f"Expected Authorization token: Bearer {WEBHOOK_AUTH_TOKEN}")
    # logger.info(f"Received Authorization header length: {len(auth_header)}")
    # logger.info(f"Expected Authorization token length: {len(f'Bearer {WEBHOOK_AUTH_TOKEN}')}")
    # logger.info(f"Received Authorization header repr: {repr(auth_header)}")
    # logger.info(f"Expected Authorization token repr: {repr(f'Bearer {WEBHOOK_AUTH_TOKEN}')}")

    if auth_header != f"Bearer {WEBHOOK_AUTH_TOKEN}":
        logger.warning("Unauthorized request received")
        return jsonify({"error": "Unauthorized"}), 403

    if data.get('typeWebhook') != 'incomingMessageReceived':
        logger.info(f"Ignored non-message webhook: {data.get('typeWebhook')}")
        return jsonify(success=True)

    try:
        chat_id = data['senderData']['chatId']
        message_id = data['idMessage']
        message_data = data.get('messageData', {})

        # Handle different message types
        if 'textMessageData' in message_data:
            body = message_data['textMessageData']['textMessage'].strip()
        elif 'extendedTextMessageData' in message_data:
            body = message_data['extendedTextMessageData']['text'].strip()
        else:
            logger.info(f"Ignored unsupported message type: {message_data.get('typeMessage')}")
            return jsonify(success=True)

    except KeyError as e:
        logger.error(f"Missing key in data: {e}")
        return jsonify({"error": f"Missing key in data: {e}"}), 200

    if body.lower().startswith('/imagine'):
        prompt = body.replace('/imagine', '').strip()
        if not prompt:
            send_message(message_id, chat_id, "Please provide a prompt after /imagine.")
            logger.info(f"Chat ID: {chat_id} - Sent Message: Please provide a prompt after /imagine.")
        else:
            send_message(message_id, chat_id, "Generating...")
            logger.info(f"Chat ID: {chat_id} - Sent Message: Generating...")
            threading.Thread(target=handle_image_generation, args=(message_id, chat_id, prompt)).start()
    else:
        threading.Thread(target=response_text, args=(message_id, chat_id, body)).start()
        logger.info(f"Chat ID: {chat_id} - Received Message: {body}")

    return jsonify(success=True)

if __name__ == '__main__':
    try:
        logger.info("Starting bot")
        app.run(debug=True, port=PORT, host="0.0.0.0")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        raise
