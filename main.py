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
        bot.reply_to(message, import os
import telebot
from flask import Flask, request
from openai import OpenAI

# ==============================
# ENVIRONMENT VARIABLES
# ==============================

BOT_TOKEN = os.environ.get("bot_token")
HF_TOKEN = os.environ.get("hf_token")

if not BOT_TOKEN:
    raise ValueError("Missing bot_token environment variable.")

if not HF_TOKEN:
    raise ValueError("Missing hf_token environment variable.")


# ==============================
# TELEGRAM BOT
# ==============================

bot = telebot.TeleBot(BOT_TOKEN)


# ==============================
# HUGGING FACE AI
# ==============================

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)


# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Bot is alive and running!", 200


# ==============================
# TELEGRAM WEBHOOK
# ==============================

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    try:
        data = request.get_data().decode("utf-8")

        update = telebot.types.Update.de_json(data)

        bot.process_new_updates([update])

        return "OK", 200

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ERROR", 500


# ==============================
# START / HELP
# ==============================

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):

    bot.reply_to(
        message,
        "Hello! 👋\n\n"
        "I am your AI chatbot.\n"
        "Ask me anything! 🤖"
    )


# ==============================
# AI CHAT
# ==============================

@bot.message_handler(
    func=lambda message: message.text is not None
)
def handle_message(message):

    try:

        # Typing indicator
        bot.send_chat_action(
            message.chat.id,
            "typing"
        )

        # Ask Hugging Face AI
        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Answer clearly and accurately. "
                        "You can understand Hindi, English and Hinglish."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ],

            max_tokens=500
        )

        # Get AI response
        reply = response.choices[0].message.content

        if not reply:
            reply = "Sorry, I couldn't generate a response."

        # Send response to Telegram
        bot.reply_to(
            message,
            reply
        )

    except Exception as e:

        print("AI ERROR:", repr(e))

        bot.reply_to(
            message,
            "❌ AI se response lene me problem aa gayi.\n"
            "Please try again."
        )


# ==============================
# START SERVER
# ==============================

if __name__ == "__main__":

    RENDER_EXTERNAL_URL = os.environ.get(
        "RENDER_EXTERNAL_URL"
    )

    if RENDER_EXTERNAL_URL:

        # Remove old webhook
        bot.remove_webhook()

        # Set new webhook
        webhook_url = (
            f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
        )

        bot.set_webhook(
            url=webhook_url
        )

        print(
            f"Webhook set to: {RENDER_EXTERNAL_URL}"
        )

    else:

        # Local testing
        bot.remove_webhook()

        import threading

        threading.Thread(
            target=bot.infinity_polling,
            daemon=True
        ).start()

        print(
            "Running in polling mode..."
        )

    # Render PORT
    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
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
