import asyncio
import os
import re
import logging
from together import Together
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

# Set Together API key
os.environ["TOGETHER_API_KEY"] = "cd2590acea8da2169498803d15ebd46c72b6cde76f73b34ec22dd656c2e0f568"
client = Together(api_key=os.environ["TOGETHER_API_KEY"])

TELEGRAM_TOKEN = "7813314372:AAGCtHA0-Wr_EcE14LnfFFqfrkS-4-r4MoA"

# Logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

# Greeting keywords
greeting_keywords = ["hi", "hello", "hey", "yo", "namaste"]

# Generate smart & friendly response
def get_together_response(prompt):
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen3-235B-A22B-fp8-tput",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu ek desi, smart aur friendly dost hai. Hinglish me baat kar. "
                        "Choti baat ka chota jawab de, aur jab user kuch bada ya serious puche tabhi lamba reply de. "
                        "Thoda mazak bhi kar sakta hai kabhi kabhi, par spam mat kar. "
                        "Kabhi bhi apne API, backend ya creator ke baare me baat mat kar."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)

        # If reply too long for a simple prompt, cut it
        if len(reply.split()) > 50 and not any(q in prompt.lower() for q in ["explain", "what is", "tell me", "kaise", "kyu", "kyon", "bata"]):
            reply = "Bhai seedhi baat bata 😅 chhota sawaal chhota jawaab."

        return reply
    except Exception as e:
        print(f"Error: {e}")
        return "Mujhe samajh nahi aaya bhai 😶"

# Message handler
async def handle_message(update: Update, context):
    message = update.message
    chat_id = message.chat_id
    text = message.text.strip().lower()

    # 1. Always reply to "hi", "hello", etc.
    if text in greeting_keywords:
        await context.bot.send_message(chat_id=chat_id, text="Hello bhai 👋 kya haal chaal?")
        return

    # 2. Only respond if someone replied to the bot
    if not message.reply_to_message or message.reply_to_message.from_user.id != context.bot.id:
        return

    # 3. Smart reply
    response = get_together_response(text)
    if not response:
        response = "Mujhe nahi pata bhai 😶"
    await context.bot.send_message(chat_id=chat_id, text=response)

# Bot runner
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    await application.run_polling(allowed_updates=None)

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
