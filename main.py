import os
import telebot
from flask import Flask, request
from openai import OpenAI

# Fetch tokens from Environment Variables
BOT_TOKEN = os.environ.get('bot_token')
HF_TOKEN = os.environ.get('hf_token')

if not BOT_TOKEN or not HF_TOKEN:
    raise ValueError("Missing 'bot_token' or 'hf_token' in environment variables.")

# Initialize the Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize OpenAI Client to point to Hugging Face's serverless inference API
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key=HF_TOKEN
)

# Initialize Flask app (required to keep the Render Web Service running)
app = Flask(__name__)

# Render Health Check URL
@app.route('/', methods=['GET'])
def index():
    return "Bot is alive and running!", 200

# Telegram Webhook Route
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    # Receive updates from Telegram and pass to the bot
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

# Handle /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am an AI chatbot. Ask me anything!")

# Handle all other text messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Show 'typing...' status in Telegram
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Query the Hugging Face AI Model via the OpenAI client
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3", # You can change this to any supported HF Chat model
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )
        
        # Extract the reply and send it back to the user
        reply = response.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, "Sorry, I encountered an error while thinking. Please try again.")
        print(f"Error: {e}")

if __name__ == '__main__':
    # Render automatically provides this environment variable
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    
    if RENDER_EXTERNAL_URL:
        # Set up Telegram Webhook
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")
        print(f"Webhook set to {RENDER_EXTERNAL_URL}")
    else:
        # Fallback to polling for local testing
        bot.remove_webhook()
        import threading
        threading.Thread(target=bot.infinity_polling).start()
        print("Running in polling mode (Local)...")

    # Render gives a specific PORT to bind to
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
