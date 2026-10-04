import os
import threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. FLASK WEB SERVER (For 24/7 Uptime via UptimeRobot) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "HYDRA ForceSub Bot Active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- 2. CONFIGURATION (Already Filled) ---
BOT_TOKEN = "8832229855:AAEOXxzWf3nPLDAAWD_tZk87stt_HlHTyIk"
CHANNEL_USERNAME = "@HydraEscrowService"
GROUP_USERNAME = "@HydraEscrow"

bot = telebot.TeleBot(BOT_TOKEN)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def check_channel_subscription(message):
    # Yeh ensure karega ki bot sirf aapke official group par hi chale
    if message.chat.username and f"@{message.chat.username}".lower() != GROUP_USERNAME.lower():
        return
    
    user_id = message.from_user.id
    
    # Group Admins ke messages check nahi honge
    try:
        chat_member = bot.get_chat_member(message.chat.id, user_id)
        if chat_member.status in ['creator', 'administrator']:
            return
    except Exception:
        pass

    # Agar user ne channel join nahi kiya hai
    if not is_subscribed(user_id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        
        markup = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton("📢 Join Official Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        markup.add(join_btn)
        
        bot.send_message(
            message.chat.id,
            f"⚠️ **[{message.from_user.first_name}](tg://user?id={user_id})**, group me message karne ke liye pehle official channel **{CHANNEL_USERNAME}** join karein!",
            parse_mode="Markdown",
            reply_markup=markup
        )

# --- 3. START SERVICES ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("HYDRA ForceSub Bot started successfully...")
    bot.infinity_polling()
  
