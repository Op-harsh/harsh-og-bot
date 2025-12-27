import logging
import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
# Tera Bot Token aur User ID yaha daal
BOT_TOKEN = "8544305886:AAE7jygimPTv555IPuTeqv91sRMTgTF1_yo"
HARSH_USER_ID = 8483875806

# Logging setup (Error dekhne ke liye)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Roast Lines (50 Lines List) ---
ROAST_LINES = [
    "Na mujhe nhi lagta tumhara jee hoga.",
    "Abey oye! Kya kar raha hai tu? Padhai kar! 😡",
    "5 minute mein 10 message bhej diye! Itni speed numericals me dikha!",
    "Padhle bhai, OBC hai tu, reservation mila hai to izzat rakh le!",
    "General walon ki halat dekhi hai? Khoon ke aansu rote hain wo.",
    "Tere paas mauka hai, mauke pe chauka maar de.",
    "Class 12 hai tera, boards bhi hain sar pe.",
    "JEE Mains aa raha hai, aur tu yaha chatting pel raha hai?",
    "PW ka Lakshya batch liya hai na? Paise barbaad mat kar.",
    "Alakh sir kya sochenge agar unka student yaha time pass karega?",
    "Rajwant sir ka danda yaad hai na? 'Htt bsdk' bolenge wo!",
    "Mummy Papa ko kya bolega result ke din?",
    "Papa wo net slow tha? Nahi chalega bahana!",
    "Backlog tera pahad ban chuka hai, aur tu yaha hai.",
    "Revision tera zero hai bhai, sharam kar le.",
    "Mock test me number aa nahi rahe, aur neta ban raha hai.",
    "Aur tujhe neta banna hai group ka? Rank la pehle.",
    "IIT Bombay ka sapna sapna hi reh jayega aise to.",
    "NIT bhi nahi milega agar yahi haal raha.",
    "Private college me 20 lakh dene hain kya baap ke?",
    "Nahi na? To phone fek aur kitab utha!",
    "Organic Chemistry bhool jayega 2 din me agar revise nahi kiya.",
    "Physics ke formula yaad hain? Rotational Motion hilta nahi tujhse!",
    "Maths me Calculus teri le lega agar practice nahi ki.",
    "Nawada ka naam roshan karna hai ya dubona hai?",
    "Padhosi ka ladka IIT nikal lega aur tu yahi reh jayega.",
    "Admin banne se ghar nahi chalta, rank lane se chalta hai.",
    "Insta scroll karna band kar aur copy khol.",
    "Telegram pe bakchodi band kar de bhai.",
    "Ye last warning hai tujhe, sudhar ja.",
    "Agli baar dikha online to phone format kar dunga (mazak hai, par dar ja).",
    "Soch us din ke baare me jab result aayega.",
    "List me naam dhundega aur 'Not Qualified' dikhega.",
    "Kaisa lagega tab? Dil tootega na?",
    "Mummy ki aankho me wo umeed dekh bhai.",
    "Papa ki mehnat ki kamayi dekh, unhone batch dilaya hai.",
    "Isliye nahi ki tu yaha bot ke sath khele.",
    "Abhi bhi time hai, sudhar ja.",
    "4 mahine ghiss ke padh le, life set hai.",
    "Warna puri zindagi private job me dhakke khayega.",
    "10 hazar ki naukri ke liye 10 ghante kaam karega?",
    "Wo chahiye kya? Nahi na? To padhne baith.",
    "To ban ja IITian! Dikha de duniya ko.",
    "Bihar ka khoon hai, aise waste mat kar.",
    "Chal shabash, ab phone rakh aur padh.",
    "Copy khol, pen utha, question laga.",
    "Jo karna hai kar bas yaha mat dikh abhi.",
    "Jaa raha hai ya main aur sunaun?",
    "Bhaag yaha se PADHNE! 🏃‍♂️💨",
    "JAA RE HARSH! PADHAI KAR! 📚🔥"
]

# --- Helper Function for Delayed Delete ---
async def delete_message_delayed(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    """Wait for 'delay' seconds and then delete the message."""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning(f"Message delete nahi hua: {e}")

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text("Bot ready hai bhai! /promoteharsh use kar promote hone ke liye!")

async def promote_harsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main promote command - Checks permissions and shows menu"""
    # Check if user is Harsh
    if update.effective_user.id != HARSH_USER_ID:
        await update.message.reply_text("Arre bhai, ye sirf Harsh ke liye hai! 😅")
        return
    
    # Check if bot is admin
    chat_id = update.effective_chat.id
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        if bot_member.status != 'administrator' or not bot_member.can_promote_members:
            await update.message.reply_text("Bhai pehle mujhe admin banao with 'Add new admins' permission! 🤖")
            return
    except Exception as e:
        await update.message.reply_text(f"Error checking bot permissions: {e}")
        return
    
    # Permission selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("All Permissions 🚀", callback_data="all_perms"),
            InlineKeyboardButton("Custom Select 🎯", callback_data="custom_perms")
        ],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Bhai, konse permissions chahiye? 🤔", 
        reply_markup=reply_markup
    )

async def permission_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle permission buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Cancelled bhai! 👍")
        context.user_data.clear()
        return
    
    if query.data == "all_perms":
        # Ask for custom title
        await query.edit_message_text("Admin title kya rakhna hai? (reply kar de)")
        context.user_data['promotion_type'] = 'all'
        context.user_data['waiting_for_title'] = True
        
    elif query.data == "custom_perms":
        # Show individual permission options
        keyboard = [
            [
                InlineKeyboardButton("Delete Messages 🗑️", callback_data="perm_delete"),
                InlineKeyboardButton("Ban Users 🔨", callback_data="perm_ban")
            ],
            [
                InlineKeyboardButton("Pin Messages 📌", callback_data="perm_pin"),
                InlineKeyboardButton("Change Info ✏️", callback_data="perm_info")
            ],
            [
                InlineKeyboardButton("Invite Users 👥", callback_data="perm_invite"),
                InlineKeyboardButton("Add Admins 👑", callback_data="perm_admin")
            ],
            [
                InlineKeyboardButton("Done ✅", callback_data="custom_done"),
                InlineKeyboardButton("Cancel ❌", callback_data="cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['selected_perms'] = []
        await query.edit_message_text(
            "Permissions select kar (multiple select kar sakta hai):", 
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("perm_"):
        # Toggle permission selection
        perm_map = {
            "perm_delete": "can_delete_messages",
            "perm_ban": "can_restrict_members", 
            "perm_pin": "can_pin_messages",
            "perm_info": "can_change_info",
            "perm_invite": "can_invite_users",
            "perm_admin": "can_promote_members"
        }
        
        selected = context.user_data.get('selected_perms', [])
        perm_name = perm_map[query.data]
        
        if perm_name in selected:
            selected.remove(perm_name)
            status = "❌"
        else:
            selected.append(perm_name)
            status = "✅"
            
        context.user_data['selected_perms'] = selected
        await query.answer(f"Permission {status}")
        
    elif query.data == "custom_done":
        await query.edit_message_text("Admin title kya rakhna hai? (reply kar de)")
        context.user_data['promotion_type'] = 'custom'
        context.user_data['waiting_for_title'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles ALL text messages.
    1. Checks if we are waiting for an Admin Title.
    2. Checks if Harsh is spamming messages (Roast logic).
    """
    user_id = update.effective_user.id
    
    # ---------------------------------------------------------
    # PART 1: Handle Admin Title Input (Promotion Logic)
    # ---------------------------------------------------------
    if context.user_data.get('waiting_for_title'):
        title = update.message.text
        promotion_type = context.user_data.get('promotion_type')
        
        try:
            # Promote user based on selection
            if promotion_type == 'all':
                await context.bot.promote_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=HARSH_USER_ID,
                    can_change_info=True,
                    can_delete_messages=True,
                    can_invite_users=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    is_anonymous=False
                )
            else: # custom
                selected_perms = context.user_data.get('selected_perms', [])
                await context.bot.promote_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=HARSH_USER_ID,
                    can_change_info='can_change_info' in selected_perms,
                    can_delete_messages='can_delete_messages' in selected_perms,
                    can_invite_users='can_invite_users' in selected_perms,
                    can_restrict_members='can_restrict_members' in selected_perms,
                    can_pin_messages='can_pin_messages' in selected_perms,
                    can_promote_members='can_promote_members' in selected_perms,
                    is_anonymous=False
                )
            
            # Set custom title (separate API call)
            try:
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=update.effective_chat.id,
                    user_id=HARSH_USER_ID,
                    custom_title=title[:16]  # Telegram limit 16 chars
                )
            except Exception as e:
                logger.warning(f"Could not set custom title: {e}")
            
            await update.message.reply_text(f"🎉 **Hogaya bhai!** Ab tu admin hai with title: '{title}' 👑")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error aaya bhai: {str(e)}")
        
        # Clear user data after promotion attempt
        context.user_data.clear()
        return # Exit function so we don't trigger spam check on the title message

    # ---------------------------------------------------------
    # PART 2: Spam Detection & Roast Logic (Only for Harsh)
    # ---------------------------------------------------------
    if user_id == HARSH_USER_ID:
        current_time = datetime.now()
        
        # Initialize timestamp list if not exists
        if 'msg_timestamps' not in context.user_data:
            context.user_data['msg_timestamps'] = []
            
        # Add current message time
        context.user_data['msg_timestamps'].append(current_time)
        
        # Filter: Keep only messages from last 5 minutes
        five_mins_ago = current_time - timedelta(minutes=5)
        context.user_data['msg_timestamps'] = [
            t for t in context.user_data['msg_timestamps'] 
            if t > five_mins_ago
        ]
        
        # Check count
        msg_count = len(context.user_data['msg_timestamps'])
        
        # If 8 or more messages (TRIGGER CHANGED TO 8)
        if msg_count >= 8:
            # Pick ONE random line from the list
            random_line = random.choice(ROAST_LINES)
            
            # Send the Roast
            warning_msg = await update.message.reply_text(
                f"@{update.effective_user.username} {random_line}"
            )
            
            # Reset counter immediately (taaki har agle msg pe roast na kare)
            context.user_data['msg_timestamps'] = []
            
            # Delete the roast message after 60 seconds (DELAY CHANGED TO 60)
            asyncio.create_task(
                delete_message_delayed(
                    context, 
                    warning_msg.chat_id, 
                    warning_msg.message_id, 
                    60
                )
            )

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("promoteharsh", promote_harsh))
    application.add_handler(CallbackQueryHandler(permission_callback))
    
    # Message Handler for Text (Handles Title Input + Spam Check)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
