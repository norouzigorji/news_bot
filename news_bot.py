import requests
from lxml import html
from telebot import TeleBot
import time
import sqlite3
import schedule

# تنظیمات ربات تلگرام
channel_id = 'YOUR_CHANNEL_ID'  # جایگزین با شناسه واقعی کانال
bot_token = 'YOUR_BOT_TOKEN_HERE'  # جایگزین با توکن واقعی ربات
bot = TeleBot(bot_token)

# URL و XPaths های مورد نیاز
BASE_URL = "https://www.bloghnews.com"
NEWS_PAGE_URL = BASE_URL + "/"
XPATH_LINK = "//div[@class='news-title']/a/@href"
XPATH_DATE = "//div[@class='news-date']/text()"
XPATH_TITLE = "//div[@class='news-title']/a/text()"
XPATH_IMAGE = "//div[@class='news-pic']/img/@src"
XPATH_LEAD = "//div[@class='news-lead']/text()"

# تنظیمات پایگاه داده SQLite
conn = sqlite3.connect('news_bot.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        url TEXT
    )
''')
conn.commit()

# تابع ذخیره اخبار در پایگاه داده
def save_news_to_db(title, url):
    try:
        cursor.execute('INSERT INTO news (title, url) VALUES (?, ?)', (title, url))
        conn.commit()
    except sqlite3.IntegrityError:
        # اگر خبر قبلاً ذخیره شده باشد، خطا را نادیده بگیر
        pass

# تابع دریافت اخبار
def get_news():
    response = requests.get(NEWS_PAGE_URL)
    tree = html.fromstring(response.content)
    links = tree.xpath(XPATH_LINK)
    dates = tree.xpath(XPATH_DATE)
    titles = tree.xpath(XPATH_TITLE)
    images = tree.xpath(XPATH_IMAGE)
    
    news_items = []
    for link, date, title, image in zip(links, dates, titles, images):
        news_url = BASE_URL + link
        news_response = requests.get(news_url)
        news_tree = html.fromstring(news_response.content)
        lead = news_tree.xpath(XPATH_LEAD)[0]
        news_items.append({
            'title': title,
            'date': date,
            'lead': lead,
            'url': news_url,
            'image': BASE_URL + image
        })
    return news_items

# تابع ارسال اخبار
def send_news(news_item):
    message = f"""
🔻{news_item['title']}

🔸{news_item['lead']}

{news_item['url']}

{news_item['date']}

🔻مرجع خبری #بلاغ_مازندران👇 
🌐 bloghnews.com 
🇮🇷 @blogh_news
"""
    bot.send_photo(channel_id, news_item['image'], caption=message)

# تابع بررسی و ارسال اخبار جدید
def fetch_and_send_news():
    news_items = get_news()
    for news_item in news_items:
        # بررسی اینکه آیا خبر قبلاً ارسال شده است
        cursor.execute('SELECT 1 FROM news WHERE title = ?', (news_item['title'],))
        if cursor.fetchone() is None:
            send_news(news_item)
            save_news_to_db(news_item['title'], news_item['url'])
            break

# تنظیم زمان‌بندی برای اجرای هر یک ساعت
schedule.every(1).hour.do(fetch_and_send_news)

# اجرای اولین بار
fetch_and_send_news()

# اجرای دائمی
while True:
    schedule.run_pending()
    time.sleep(1)
