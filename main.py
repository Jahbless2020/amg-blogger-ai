from write_secrets import write_file_from_b64_env
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from config import TELEGRAM_TOKEN
import ai_writer
import blogger

# Write credentials.json and token.json from base64 env vars if provided
# This allows secure storage of JSON files in environment variables (base64 encoded)
write_file_from_b64_env("B64_CREDENTIALS_JSON", "credentials.json")
write_file_from_b64_env("B64_TOKEN_JSON", "token.json")

# Helper: split long messages into Telegram-safe chunks (~3900 chars)
def split_chunks(text, max_len=3900):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        # Try to split on a newline or space for cleaner breaks
        if end < len(text):
            # find last newline or space before end
            split_at = text.rfind("\n", start, end)
            if split_at <= start:
                split_at = text.rfind(" ", start, end)
            if split_at <= start:
                split_at = end
            end = split_at
        chunks.append(text[start:end].strip())
        start = end
    return chunks


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 AMG Blogger AI is online!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start\n/help\n/write <topic> — generate article\n/publish — publish last article to Blogger (requires token.json)")


# /write <topic>
async def write_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /write <topic>")
        return

    topic = " ".join(context.args)
    await update.message.reply_text(f"Generating article about: {topic} — this may take a few seconds...")

    loop = asyncio.get_running_loop()
    try:
        # Run the blocking ai_writer in an executor
        article_html = await loop.run_in_executor(None, ai_writer.write_article, topic)
    except Exception as e:
        await update.message.reply_text(f"Error while generating article: {e}")
        return

    # Save the last generated article in application data (optional)
    context.application.bot_data.setdefault("last_articles", {})
    # store per-chat so /publish is unambiguous
    context.application.bot_data["last_articles"][update.effective_chat.id] = {
        "title": topic,
        "content": article_html
    }

    # Send HTML content in chunks
    chunks = split_chunks(article_html)
    for chunk in chunks:
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception:
            # Fallback to plain text if HTML parsing fails
            await update.message.reply_text(chunk)


# /publish - publishes last generated article for this chat to Blogger
async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chats_store = context.application.bot_data.get("last_articles", {})
    saved = chats_store.get(update.effective_chat.id)
    if not saved:
        await update.message.reply_text("No generated article found for this chat. Use /write <topic> first.")
        return

    title = saved.get("title", "AI Article")
    content = saved.get("content", "")

    # Load credentials from token.json (see README notes). If not available, error out.
    credentials = None
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
    # Call the blogger wrapper (which uses the credentials)
    try:
        result = await loop.run_in_executor(None, blogger.publish_post, title, content, credentials)
        await update.message.reply_text("Published to Blogger successfully.")
    except Exception as e:
        await update.message.reply_text(f"Failed to publish: {e}")


def main():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN not set in environment.")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("write", write_command))
    app.add_handler(CommandHandler("publish", publish_command))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
