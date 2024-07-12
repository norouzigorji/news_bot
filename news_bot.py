import sqlite3
import requests
import time
from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.error import TelegramError

class NewsBot:
    def __init__(self, token, admin_id):
        self.bot = Bot(token=token)
        self.admin_id = str(admin_id)
        self.base_url = 'https://www.bloghnews.com/news'
        self.conn = sqlite3.connect('news_bot.db', check_same_thread=False)
        self.create_tables()
        self.current_channel = None
        self.delay_seconds = None

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS channels (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    chat_id TEXT NOT NULL,
                                    delay INTEGER NOT NULL)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS news (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    channel_id INTEGER NOT NULL,
                                    news_id TEXT NOT NULL,
                                    FOREIGN KEY (channel_id) REFERENCES channels (id))''')

    def start(self, update: Update, context):
        if str(update.message.chat_id) == self.admin_id:
            keyboard = [
                [InlineKeyboardButton("افزودن کانال", callback_data='add_channel')],
                [InlineKeyboardButton("حذف کانال", callback_data='delete_channel')],
                [InlineKeyboardButton("جستجوی کانال با نام", callback_data='search_channel')],
                [InlineKeyboardButton("نمایش اطلاعات کانال", callback_data='show_channel_info')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('منوی اصلی', reply_markup=reply_markup)
        else:
            update.message.reply_text('شما دسترسی ندارید')

    def button(self, update: Update, context):
        query = update.callback_query
        query.answer()
        if query.data == 'add_channel':
            context.bot.send_message(chat_id=query.message.chat_id, text='لطفاً آیدی عددی کانال را وارد کنید:')
            context.user_data['state'] = 'waiting_for_channel_id'
        elif query.data == 'delete_channel':
            context.bot.send_message(chat_id=query.message.chat_id, text='لطفاً آیدی عددی کانال را وارد کنید:')
            context.user_data['state'] = 'waiting_for_delete_channel_id'
        elif query.data == 'search_channel':
            context.bot.send_message(chat_id=query.message.chat_id, text='لطفاً نام کانال را وارد کنید:')
            context.user_data['state'] = 'waiting_for_search_channel'
        elif query.data == 'show_channel_info':
            context.bot.send_message(chat_id=query.message.chat_id, text='لطفاً آیدی عددی کانال را وارد کنید:')
            context.user_data['state'] = 'waiting_for_channel_info'

    def handle_message(self, update: Update, context):
        state = context.user_data.get('state')
        if state == 'waiting_for_channel_id':
            self.current_channel = update.message.text
            keyboard = [
                [InlineKeyboardButton("افزودن ربات به کانال", callback_data='add_bot_to_channel')],
                [InlineKeyboardButton("تنظیمات زمان", callback_data='set_time')],
                [InlineKeyboardButton("تایید", callback_data='confirm_channel')],
                [InlineKeyboardButton("بازگشت", callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('تنظیمات کانال', reply_markup=reply_markup)
        elif state == 'waiting_for_delete_channel_id':
            chat_id = update.message.text
            with self.conn:
                self.conn.execute('DELETE FROM channels WHERE chat_id = ?', (chat_id,))
            update.message.reply_text('کانال حذف شد.')
            context.user_data['state'] = None
        elif state == 'waiting_for_search_channel':
            name = update.message.text
            cursor = self.conn.execute('SELECT * FROM channels WHERE chat_id LIKE ?', ('%' + name + '%',))
            results = cursor.fetchall()
            response = 'نتایج:\n'
            for row in results:
                response += f"{row[1]} - {row[2]}\n"
            update.message.reply_text(response)
            context.user_data['state'] = None
        elif state == 'waiting_for_channel_info':
            chat_id = update.message.text
            cursor = self.conn.execute('SELECT * FROM channels WHERE chat_id = ?', (chat_id,))
            result = cursor.fetchone()
            if result:
                response = f"آیدی عددی: {result[1]}\nزمان مکث: {result[2]} دقیقه\n"
                update.message.reply_text(response)
            else:
                update.message.reply_text('کانال یافت نشد.')
            context.user_data['state'] = None

    def handle_callback(self, update: Update, context):
        query = update.callback_query
        query.answer()
        if query.data == 'add_bot_to_channel':
            query.edit_message_text(text="ربات به کانال اضافه شد. لطفاً زمان مکث را تنظیم کنید.")
        elif query.data == 'set_time':
            keyboard = [
                [InlineKeyboardButton("1 دقیقه", callback_data='set_1')],
                [InlineKeyboardButton("5 دقیقه", callback_data='set_5')],
                [InlineKeyboardButton("10 دقیقه", callback_data='set_10')],
                [InlineKeyboardButton("30 دقیقه", callback_data='set_30')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text="لطفاً زمان مکث را انتخاب کنید:", reply_markup=reply_markup)
        elif query.data.startswith('set_'):
            self.delay_seconds = int(query.data.split('_')[1]) * 60
            query.edit_message_text(text=f"زمان مکث {self.delay_seconds // 60} دقیقه تنظیم شد.")
        elif query.data == 'confirm_channel':
            with self.conn:
                self.conn.execute('INSERT INTO channels (chat_id, delay) VALUES (?, ?)', (self.current_channel, self.delay_seconds // 60))
            query.edit_message_text(text="کانال اضافه شد.")
            self.current_channel = None
            self.delay_seconds = None
        elif query.data == 'main_menu':
            self.start(update, context)

    def get_latest_news(self, channel_id):
        response = requests.get(self.base_url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        news_elements = soup.select("div.special-title a")
        if not news_elements:
            return None
        latest_news_url = news_elements[0]['href']
        latest_news_id = latest_news_url.split('/')[-1].split('-')[0]
        cursor = self.conn.execute('SELECT news_id FROM news WHERE channel_id = ? ORDER BY id DESC LIMIT 1', (channel_id,))
        result = cursor.fetchone()
        if result is None or latest_news_id > result[0]:
            with self.conn:
                self.conn.execute('INSERT INTO news (channel_id, news_id) VALUES (?, ?)', (channel_id, latest_news_id))
            return self.base_url + latest_news_url
        return None

    def fetch_news_details(self, news_url):
        response = requests.get(news_url)
        if response.status_code != 200:
            return None, None, None, None
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select_one("div.special-title a").text.strip()
        lead_text = soup.select_one("div.first-abs.hidden-xs.arch_abs").text.strip()
        date_time = soup.select_one("div.black-text-clock").text.strip()
        image_url = soup.select_one("div.special-img.service-img img")['src']
        return title, lead_text, date_time, image_url

    def format_message(self, title, lead_text, news_url, date_time):
        message = f"""
🔻{title}

🔸{lead_text}

{news_url}

{date_time}

🔻مرجع خبری #بلاغ_مازندران👇 
🌐 bloghnews.com 
🇮🇷 {self.bot.username}
"""
        return message

    def send_news_to_channel(self, chat_id, message, image_url):
        try:
            self.bot.send_photo(chat_id=chat_id, photo=image_url, caption=message)
        except TelegramError as e:
            print(f"Error sending message: {e}")

    def run(self):
        while True:
            cursor = self.conn.execute('SELECT * FROM channels')
            channels = cursor.fetchall()
            for channel in channels:
                latest_news_url = self.get_latest_news(channel[0])
                if latest_news_url:
                    title, lead_text, date_time, image_url = self.fetch_news_details(latest_news_url)
                    if title and lead_text and date_time and image_url:
                        message = self.format_message(title, lead_text, latest_news_url, date_time)
                        self.send_news_to_channel(channel[1], message, image_url)
                time.sleep(channel[2] * 60)

if __name__ == '__main__':
    import sys
    token = sys.argv[1]
    admin_id = sys.argv[2]
    news_bot = NewsBot(token, admin_id)
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', news_bot.start))
    dp.add_handler(CallbackQueryHandler(news_bot.button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, news_bot.handle_message))
    dp.add_handler(CallbackQueryHandler(news_bot.handle_callback))
    updater.start_polling()
    updater.idle()
    news_bot.run()
