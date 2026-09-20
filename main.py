import os
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


# ==============================
# HEALTH CHECK
# ==============================

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

        print("WEBHOOK ERROR:", repr(e))

        return "ERROR", 500


# ==============================
# START / HELP COMMAND
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

        # Show typing
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
                        "You understand Hindi, English and Hinglish."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ],

            max_tokens=500
        )

        # Get AI answer
        reply = response.choices[0].message.content

        if not reply:
            reply = "Sorry, I could not generate a response."

        # Send answer
        bot.reply_to(
            message,
            reply
        )

    except Exception as e:

        # Print REAL error in Render logs
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
            "Webhook set to:",
            webhook_url
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
