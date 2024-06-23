import logging
import os
import threading
import telebot
from dotenv import load_dotenv
from llm import generate_llm
from sd import generate_sd
import time

# Load environment variables
def load_env():
    load_dotenv()
    global TELEGRAM_BOT_TOKEN
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

load_env()

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

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

def response_text(chat_id, prompt):
    """
    Generate a response using the LLM and send it to the user.
    """
    try:
        msg = generate_llm(prompt)  # Example function call to generate a response
        bot.send_message(chat_id, msg)
        logger.info(f"Chat ID: {chat_id} - Sent Message: {msg}")
    except Exception as e:
        logger.error(f"Chat ID: {chat_id} - Error in response_text: {e}")
        bot.send_message(chat_id, "There was an error processing your request.")

@bot.message_handler(commands=['imagine'])
def handle_imagine_command(message):
    """
    Handle the /imagine command by generating an image from the provided prompt.
    """
    prompt = message.text.replace('/imagine', '').strip()
    if not prompt:
        bot.reply_to(message, "Please provide a prompt after /imagine.")
        logger.info(f"Chat ID: {message.chat.id} - Sent Message: Please provide a prompt after /imagine.")
        return

    generating_message = bot.send_message(message.chat.id, "Generating...")
    logger.info(f"Chat ID: {message.chat.id} - Sent Message: Generating...")

    def handle_image_generation():
        try:
            # Example function call to generate image data
            image_data, image_path = generate_sd(prompt)
            bot.delete_message(chat_id=message.chat.id, message_id=generating_message.message_id)

            if image_data:
                bot.send_photo(message.chat.id, image_data)
                logger.info(f"Chat ID: {message.chat.id} - Sent Image {image_path}")
            else:
                bot.reply_to(message, "Failed to generate image. Please try again later.")
                logger.error(f"Chat ID: {message.chat.id} - Failed to generate image.")
        except Exception as e:
            logger.error(f"Chat ID: {message.chat.id} - Error in handle_image_generation: {e}")
            bot.reply_to(message, "There was an error generating the image. Please try again later.")

    threading.Thread(target=handle_image_generation).start()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Handle all text messages by generating a response and sending it.
    """
    chat_id = message.chat.id
    user_message = message.text
    logger.info(f"Chat ID: {chat_id} - Received Message: {user_message}")

    threading.Thread(target=response_text, args=(chat_id, user_message)).start()

def start_telegram_bot():
    """
    Start the Telegram bot.
    """
    while True:
        try:
            logger.info("Starting bot")
            bot.polling(none_stop=True)
        except Exception as e:
            logger.critical(f"Critical error: {e}")
            time.sleep(5)  # Wait for a few seconds before restarting

# Ensure the bot starts when this script is executed directly
if __name__ == '__main__':
    start_telegram_bot()
