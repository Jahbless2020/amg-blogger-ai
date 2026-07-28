"""
main.py

This version starts a small Flask app bound to the Render $PORT so the Web Service passes the port-scan check,
while running the Telegram long-polling bot in a background thread.
It also decodes B64_CREDENTIALS_JSON and B64_TOKEN_JSON at startup (if present) using write_secrets.write_file_from_b64_env.
"""

import os
import threading
import asyncio
from flask import Flask

from write_secrets import write_file_from_b64_env
from config import TELEGRAM_TOKEN
import ai_writer
import blogger

# Ensure any base64-encoded JSON secrets are written to disk at startup
write_file_from_b64_env("B64_CREDENTIALS_JSON", "credentials.json")
write_file_from_b64_env("B64_TOKEN_JSON", "token.json")

# Create a small Flask app for health checks and to bind the required port
app = Flask(__name__)

@app.route("/")
def index():
    return "OK", 200

@app.route("/health")
def health():
    return "healthy", 200


def start_flask():
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 so Render can detect the open port
    print(f"Starting Flask on 0.0.0.0:{port}")
    # Use the built-in server for simplicity on Render
    app.run(host="0.0.0.0", port=port)


# Telegram bot code (runs in background thread)
def start_bot():
    # Import here to avoid requiring these packages until this function runs
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.constants import ParseMode

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🏆 AMG Blogger AI is online!")

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("/start\n/help\n/write <topic> — generate article\n/publish — publish last article to Blogger (requires token.json)")

    async def write_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /write <topic>")
            return

        topic = " ".join(context.args)
        await update.message.reply_text(f"Generating article about: {topic} — this may take a few seconds...")

        loop = asyncio.get_running_loop()
        try:
            # Run blocking ai_writer in executor
            article_html = await loop.run_in_executor(None, ai_writer.write_article, topic)
        except Exception as e:
            await update.message.reply_text(f"Error while generating article: {e}")
            return

        # Save last article per chat
        context.application.bot_data.setdefault("last_articles", {})
        context.application.bot_data[update.effective_chat.id] = {"title": topic, "content": article_html}

        # Split into safe chunks and send
        max_len = 3900
        for i in range(0, len(article_html), max_len):
            chunk = article_html[i:i+max_len]
            try:
                await update.message.reply_text(chunk, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception:
                await update.message.reply_text(chunk)

    async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chats_store = context.application.bot_data.get("last_articles", {})
        saved = chats_store.get(update.effective_chat.id)
        if not saved:
            await update.message.reply_text("No generated article found for this chat. Use /write <topic> first.")
            return

        title = saved.get("title", "AI Article")
        content = saved.get("content", "")

        # Load credentials from token.json
        try:
            from google.oauth2.credentials import Credentials
            if os.path.exists("token.json"):
                credentials = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/blogger"])
            else:
                await update.message.reply_text("No token.json found. Generate OAuth credentials and save token.json before using /publish.")
                return
        except Exception as e:
            await update.message.reply_text(f"Error loading credentials: {e}")
            return

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, blogger.publish_post, title, content, credentials)
            await update.message.reply_text("Published to Blogger successfully.")
        except Exception as e:
            await update.message.reply_text(f"Failed to publish: {e}")

    # Build and run the application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("write", write_command))
    application.add_handler(CommandHandler("publish", publish_command))

    print("Starting Telegram polling...")
    application.run_polling()


if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()

    # Start Flask (blocks main thread and binds to PORT)
    start_flask()
