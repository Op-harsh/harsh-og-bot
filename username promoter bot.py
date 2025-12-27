import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Tera bot token aur user ID
BOT_TOKEN = "8544305886:AAE7jygimPTv555IPuTeqv91sRMTgTF1_yo"
HARSH_USER_ID = 8483875806

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text("Bot ready hai bhai! /promoteharsh use kar promote hone ke liye!")

async def promote_harsh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main promote command"""
    # Check if user is Harsh
    if update.effective_user.id != HARSH_USER_ID:
        await update.message.reply_text("Arre bhai, ye sirf Harsh ke liye hai! 😅")
        return
    
    # Check if bot is admin
    chat_id = update.effective_chat.id
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    
    if bot_member.status != 'administrator' or not bot_member.can_promote_members:
        await update.message.reply_text("Bhai pehle mujhe admin banao with 'Add new admins' permission! 🤖")
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
    """Handle permission selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Cancelled bhai! 👍")
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
    
    # Handle individual permission selection
    elif query.data.startswith("perm_"):
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
    """Handle title input"""
    if not context.user_data.get('waiting_for_title'):
        return
        
    title = update.message.text
    promotion_type = context.user_data.get('promotion_type')
    
    try:
        # Promote user based on selection
        if promotion_type == 'all':
            success = await context.bot.promote_chat_member(
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
        else:  # custom
            selected_perms = context.user_data.get('selected_perms', [])
            success = await context.bot.promote_chat_member(
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
                custom_title=title[:16]  # Max 16 characters
            )
        except Exception as e:
            logger.warning(f"Could not set custom title: {e}")
        
        await update.message.reply_text(f"🎉 **Hogaya bhai!** Ab tu admin hai with title: '{title}' 👑")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error aaya bhai: {str(e)}")
    
    # Clear user data
    context.user_data.clear()

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("promoteharsh", promote_harsh))
    application.add_handler(CallbackQueryHandler(permission_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
