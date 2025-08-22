import os
import random
import logging
import requests
from PIL import Image
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    """Send a text message to a Telegram chat"""
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=data)
    return response.json()

def send_audio(chat_id, audio_path):
    """Send an audio file to a Telegram chat"""
    url = f"{BASE_URL}/sendAudio"
    with open(audio_path, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    return response.json()

def send_document(chat_id, document_path, caption=""):
    """Send a document to a Telegram chat"""
    url = f"{BASE_URL}/sendDocument"
    with open(document_path, "rb") as doc_file:
        files = {"document": doc_file}
        data = {"chat_id": chat_id, "caption": caption}
        response = requests.post(url, files=files, data=data)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram webhook updates"""
    update = request.get_json()
    
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Handle commands
        if text.startswith("/start") or text.startswith("/help"):
            send_message(chat_id, 
                "🎁 Welcome to MagicBox Bot!\n\n"
                "I can do:\n"
                "🎵 /music - Get a sample song\n"
                "📂 /convert - Convert an image to PNG\n"
                "📝 /feedback <your text> - Send feedback\n"
                "😂 /fun - Get a random joke"
            )
        
        elif text.startswith("/music"):
            send_message(chat_id, "🎵 Here's a sample song for you!")
            send_audio(chat_id, "sample.mp3")
        
        elif text.startswith("/fun"):
            jokes = [
                "😂 Why don't skeletons fight each other? Because they don't have the guts!",
                "🤣 Parallel lines have so much in common. Too bad they'll never meet.",
                "😆 I told my computer I needed a break, and it said: 'No problem, I'll go to sleep.'"
            ]
            send_message(chat_id, random.choice(jokes))
        
        elif text.startswith("/feedback"):
            feedback_text = text.replace("/feedback", "").strip()
            if feedback_text:
                with open("feedback.txt", "a") as f:
                    f.write(f"User {chat_id}: {feedback_text}\n")
                send_message(chat_id, "✅ Thanks for your feedback!")
            else:
                send_message(chat_id, "📝 Please type your feedback after /feedback")
        
        # Handle document messages for conversion
        elif "document" in message or "photo" in message:
            send_message(chat_id, "📂 To convert this file to PNG, use the /convert command")
    
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    return 'MagicBox Bot is running!'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
