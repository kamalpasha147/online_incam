import os
import time
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার API এবং বোট টোকেন এখানে দিন
API_ID = '30778474'
API_HASH = '5c1c24ddfc8d7ae3ca421bdb1d4d2a98'
BOT_TOKEN = '7583256345:AAHhg2sfHzV0MR4W_BbQjx6Z6xiUkgrMVGw'

app = Client("ytdl_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ওয়েলকাম মেসেজ
WELCOME_TEXT = """
👋 **স্বাগতম আমাদের সুপারফাস্ট ইউটিউব ডাউনলোডার বটে!**

🚀 এই বটটি দিয়ে আপনি যেকোনো ইউটিউব ভিডিও এবং অডিও পলক ফেলতেই ডাউনলোড করতে পারবেন।

✅ **কীভাবে ব্যবহার করবেন?**
১. ইউটিউব ভিডিওর লিঙ্ক পাঠান।
২. অডিও বা ভিডিও সিলেক্ট করুন।
৩. কয়েক সেকেন্ড অপেক্ষা করুন, আপনার ফাইল রেডি!

👨‍💻 আমাদের সাথে থাকার জন্য ধন্যবাদ।
"""

# বাটন কিবোর্ড
def download_markup(url):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 ভিডিও (MP4)", callback_data=f"video|{url}")],
        [InlineKeyboardButton("🎵 অডিও (MP3)", callback_data=f"audio|{url}")]
    ])

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(WELCOME_TEXT)

@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def link_handler(client, message):
    url = message.text
    await message.reply_text("📥 **লিঙ্ক পাওয়া গেছে!** কি ডাউনলোড করতে চান?", reply_markup=download_markup(url))

@app.on_callback_query(filters.regex(r"^(video|audio)"))
async def download_handler(client, callback_query):
    choice, url = callback_query.data.split("|")
    status_msg = await callback_query.message.edit_text("⚡ **প্রোসেস শুরু হয়েছে... (১০ সেকেন্ডের মধ্যে শেষ হবে)**")

    # ফাইল নাম এবং পাথ সেট করা
    unique_id = str(int(time.time()))
    output_path = f"downloads/{unique_id}_%(title)s.%(ext)s"
    
    # দ্রুত ডাউনলোডের জন্য yt-dlp অপশন
    ydl_opts = {
        'format': 'best[ext=mp4]/best' if choice == 'video' else 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }

    if choice == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        await status_msg.edit_text("🚀 **প্রোসেস সম্পন্ন! এখন আপলোড হচ্ছে...**")
        
        # ফাইল আপলোড
        if choice == 'video':
            await client.send_video(callback_query.message.chat.id, video=filename, caption="✅ ডাউনলোড সফল!")
        else:
            await client.send_audio(callback_query.message.chat.id, audio=filename, caption="✅ ডাউনলোড সফল!")
        
        # ক্লিনআপ
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **এরর:** {str(e)}")

print("বট সফলভাবে চালু হয়েছে এবং দ্রুত কাজ করছে!")
app.run()
  
