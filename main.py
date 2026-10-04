import os
import threading
from datetime import datetime, timedelta
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

# --- 1. FLASK WEB SERVER (For 24/7 Uptime) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "HYDRA ForceSub Bot Active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- 2. BOT CONFIGURATION ---
BOT_TOKEN = "8832229855:AAEOXxzWf3nPLDAAWD_tZk87stt_HlHTyIk"
CHANNEL_USERNAME = "@HydraEscrowServices"
GROUP_USERNAME = "@HydraEscrow"

bot = telebot.TeleBot(BOT_TOKEN)

# Check if user is subscribed to channel
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

# --- 3. MESSAGE HANDLER ---
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def check_channel_subscription(message):
    # Only filter official group
    if message.chat.username and f"@{message.chat.username}".lower() != GROUP_USERNAME.lower():
        return
    
    user_id = message.from_user.id
    
    # Ignore Group Admins
    try:
        chat_member = bot.get_chat_member(message.chat.id, user_id)
        if chat_member.status in ['creator', 'administrator']:
            return
    except Exception:
        pass

    # If user (New or Old) is NOT subscribed to channel
    if not is_subscribed(user_id):
        # 1. Delete user's message
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        
        # 2. Mute user for 10 minutes (or until verified)
        mute_until = datetime.now() + timedelta(minutes=10)
        formatted_time = mute_until.strftime("%d/%m/%Y %H:%M:%S")
        
        try:
            bot.restrict_chat_member(
                message.chat.id,
                user_id,
                until_date=int(mute_until.timestamp()),
                permissions=ChatPermissions(can_send_messages=False)
            )
        except Exception:
            pass
        
        # 3. Create exact inline buttons
        markup = InlineKeyboardMarkup()
        sub_btn = InlineKeyboardButton("📣 Subscribe to channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        check_btn = InlineKeyboardButton("✅ OK | I subscribed", callback_data=f"checksub_{user_id}")
        markup.add(sub_btn)
        markup.add(check_btn)
        
        # 4. Format exact warning message
        user_name = message.from_user.first_name
        warning_text = (
            f"[{user_name}](tg://user?id={user_id}) `[{user_id}]` to be accepted in the group, "
            f"please subscribe to our channel. Once joined, click the button below.\n\n"
            f"Action: Muted 🔇 until **{formatted_time}**."
        )
        
        try:
            bot.send_message(message.chat.id, warning_text, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            pass

# --- 4. BUTTON CLICK HANDLER (VERIFICATION) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("checksub_"))
def handle_sub_callback(call):
    target_user_id = int(call.data.split("_")[1])
    clicker_id = call.from_user.id
    
    # Check if the right person clicked the button
    if clicker_id != target_user_id:
        bot.answer_callback_query(call.id, "⚠️ Yeh button aapke liye nahi hai!", show_alert=True)
        return

    # Re-check channel subscription status
    if is_subscribed(clicker_id):
        # Unmute user
        try:
            bot.restrict_chat_member(
                call.message.chat.id,
                clicker_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
        except Exception:
            pass
        
        bot.answer_callback_query(call.id, "✅ Aapne channel join kar liya hai! Ab aap group me message kar sakte hain.", show_alert=True)
        
        # Delete the bot warning message
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai! Pehle subscribe karein.", show_alert=True)

# --- 5. START SERVICES ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("HYDRA ForceSub Bot started successfully...")
    bot.infinity_polling()
    
