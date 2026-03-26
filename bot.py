import logging
import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
BOT_TOKEN = "8544305886:AAE7jygimPTv555IPuTeqv91sRMTgTF1_yo"
HARSH_USER_ID = 8483875806

MAX_DAILY_MESSAGES = 100
MUTE_DURATION_HOURS = 12

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Roast Lines (Pehle wali hi hain) ---
ROAST_LINES = [
    "Na mujhe nhi lagta tumhara jee hoga.",
    "rj sir ka danda dekha hai?? ha whi apne wha daal lo chomu"
    "padhle warna nali ka keeda bankr rh jaiga"
    "hass kya rha chomu , padhle!!"
    "tum jisko reply kiya wo dharti ka bojh hai bade wala  (execpt agar koi didi hai to)"
    "bhai blow job krna padega agar padhai nhi kiye to"
    " tumse gf na banegi. kyuki tum collage nhi ja paoge"
    " collage ke sath sex krna hai to kalam uthao"
    "kalam chalao juban nhi"
    "abe ohh machhar ka jhaat padhle"
    "hass kya rha hai gandu"
    "bas ek bar socho collage jane ke baad kya life hoge"
    "lagta hai majdooro ka salary badh gya hai isliye tum majdoori krne ka soch rhe"
    "pdhle bc"
    # Baaki lines bhi tu add kar lena apne hisaab se
]

# --- Helper Function ---
async def delete_message_delayed(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning(f"Message delete nahi hua: {e}")

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarvis ready hai bhai! Padhle warna bot kya, Alakh sir bhi nahi bacha payenge! /promoteharsh use kar.")

async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows how many messages Harsh has sent today"""
    if update.effective_user.id != HARSH_USER_ID:
        return

    now = datetime.now()
    today = now.date()

    # Agar aaj ka date nahi hai data me, toh reset kar do
    if 'msg_date' not in context.user_data or context.user_data['msg_date'] != today:
        context.user_data['msg_date'] = today
        context.user_data['daily_msg_count'] = 0

    count = context.user_data.get('daily_msg_count', 0)
    remaining = MAX_DAILY_MESSAGES - count
    
    if remaining <= 0:
        await update.message.reply_text("🚨 Tera aaj ka quota khatam! Tu mute ho chuka hai 12 ghante ke liye. Padhle ab!")
    else:
        await update.message.reply_text(f"📊 Tera aaj ka hisaab:\n✉️ Messages sent: {count}/{MAX_DAILY_MESSAGES}\n⏳ Bache hue: {remaining}\n\nLimit cross ki to seedha 12 ghante ka mute aur admin role gayab! ⚠️")


async def promote_harsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (Tera purana promote_harsh code same rahega yaha)
    if update.effective_user.id != HARSH_USER_ID:
        await update.message.reply_text("Arre bhai, ye sirf Harsh ke liye hai! 😅")
        return
    
    chat_id = update.effective_chat.id
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        if bot_member.status != 'administrator' or not bot_member.can_promote_members:
            await update.message.reply_text("Bhai pehle mujhe admin banao with 'Add new admins' permission! 🤖")
            return
    except Exception as e:
        await update.message.reply_text(f"Error checking bot permissions: {e}")
        return
    
    keyboard = [
        [InlineKeyboardButton("All Permissions 🚀", callback_data="all_perms"),
         InlineKeyboardButton("Custom Select 🎯", callback_data="custom_perms")],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bhai, konse permissions chahiye? 🤔", reply_markup=reply_markup)

# (Permission callback purana wala hi copy paste kar lena yaha)
async def permission_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel":
        await query.edit_message_text("Cancelled bhai! 👍")
        context.user_data.clear()
        return
    if query.data == "all_perms":
        await query.edit_message_text("Admin title kya rakhna hai? (reply kar de)")
        context.user_data['promotion_type'] = 'all'
        context.user_data['waiting_for_title'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # --- PART 1: Admin Title ---
    if context.user_data.get('waiting_for_title'):
        title = update.message.text
        try:
            await context.bot.promote_chat_member(
                chat_id=update.effective_chat.id,
                user_id=HARSH_USER_ID,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                is_anonymous=False
            )
            await context.bot.set_chat_administrator_custom_title(
                chat_id=update.effective_chat.id,
                user_id=HARSH_USER_ID,
                custom_title=title[:16] 
            )
            await update.message.reply_text(f"🎉 **Hogaya bhai!** Ab tu admin hai with title: '{title}' 👑")
        except Exception as e:
            await update.message.reply_text(f"❌ Error aaya bhai: {str(e)}")
        context.user_data.clear()
        return 

    # --- PART 2: Harsh Ka Daily Message & Spam Logic ---
    if user_id == HARSH_USER_ID:
        now = datetime.now()
        today = now.date()

        # 1. Daily Message Counter Check
        if 'msg_date' not in context.user_data or context.user_data['msg_date'] != today:
            context.user_data['msg_date'] = today
            context.user_data['daily_msg_count'] = 0

        context.user_data['daily_msg_count'] += 1
        count = context.user_data['daily_msg_count']

        # Agar 100 messages cross ho gaye
        if count == MAX_DAILY_MESSAGES:
            chat_id = update.effective_chat.id
            try:
                # Pehle Demote karo (Sari permissions False)
                await context.bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=HARSH_USER_ID,
                    can_change_info=False, can_delete_messages=False, can_invite_users=False,
                    can_restrict_members=False, can_pin_messages=False, can_promote_members=False,
                    is_anonymous=False
                )
                
                # Fir Mute karo 12 hours ke liye
                until_date = now + timedelta(hours=MUTE_DURATION_HOURS)
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=HARSH_USER_ID,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_date
                )
                
                await update.message.reply_text(
                    "🚨 **LIMIT CROSSED!** 🚨\n"
                    "100 messages poore ho gaye bhai! Maine tera admin role chheen liya hai aur 12 ghante ke liye mute kar diya hai.\n"
                    "Ab ek shabd nahi likh payega. Chup chaap phone rakh aur Physics Wallah ka lecture laga. Organic chemistry teri wait kar rahi hai! 😡📚"
                )
            except Exception as e:
                logger.error(f"Action failed: {e}")
            return # Yaha se return kar do taaki aage spam check me na jaye

        # 2. Short-term Spam Detection (8 msgs in 5 mins)
        if 'msg_timestamps' not in context.user_data:
            context.user_data['msg_timestamps'] = []
            
        context.user_data['msg_timestamps'].append(now)
        
        five_mins_ago = now - timedelta(minutes=5)
        context.user_data['msg_timestamps'] = [
            t for t in context.user_data['msg_timestamps'] if t > five_mins_ago
        ]
        
        if len(context.user_data['msg_timestamps']) >= 8:
            random_line = random.choice(ROAST_LINES)
            warning_msg = await update.message.reply_text(f"@{update.effective_user.username} {random_line}")
            
            context.user_data['msg_timestamps'] = [] # Reset
            asyncio.create_task(delete_message_delayed(context, warning_msg.chat_id, warning_msg.message_id, 60))

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Naye aur purane handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("promoteharsh", promote_harsh))
    application.add_handler(CommandHandler("count", count_messages)) # Naya command
    application.add_handler(CallbackQueryHandler(permission_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Jarvis is running... Aur Harsh padhne jaa raha hai.")
    application.run_polling()

if __name__ == '__main__':
    main()
