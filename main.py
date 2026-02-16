import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def get_ai_response(text):
    try:
        # Model ကို ပိုပြီး Stable ဖြစ်တဲ့ Gemini Pro နဲ့ စမ်းပါမယ်
        completion = client.chat.completions.create(
            model="google/gemini-pro-1.5:free",
            messages=[{"role": "user", "content": text}],
            extra_headers={"HTTP-Referer": "https://render.com"}
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Error တက်ရင် Error message ကိုပါ ပြန်ပို့ခိုင်းထားပါတယ်
        return f"❌ AI Error တက်နေတယ် ကိုကို: {str(e)[:100]}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    # Bot အလုပ်လုပ်ကြောင်း အရင်သိရအောင် Message တစ်ခု အမြန်ပို့မယ်
    await update.message.reply_text("နေခြည်ထွေးလေး စဉ်းစားနေတယ်နော်... ⏳")
    
    ai_reply = await get_ai_response(update.message.text)
    await update.message.reply_text(ai_reply)

app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

@app.route('/')
def index():
    return "Bot is Active!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
