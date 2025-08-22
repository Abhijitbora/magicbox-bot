import os
import random
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

TOKEN = os.getenv("BOT_TOKEN")  # Railway will store this

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 Welcome to MagicBox Bot!\n\n"
        "I can do:\n"
        "🎵 /music - Get a sample song\n"
        "📂 /convert - Convert an image to PNG\n"
        "📝 /feedback <your text> - Send feedback\n"
        "😂 /fun - Get a random joke\n"
    )

# /music
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Here's a sample song for you!")
    await update.message.reply_audio(InputFile("sample.mp3"))

# /convert
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file = await update.message.document.get_file()
        file_path = f"temp_{update.message.document.file_name}"
        await file.download_to_drive(file_path)

        try:
            img = Image.open(file_path)
            png_path = file_path.rsplit(".", 1)[0] + ".png"
            img.save(png_path, "PNG")
            await update.message.reply_document(InputFile(png_path))
            os.remove(png_path)
        except:
            await update.message.reply_text("⚠️ Only image files can be converted right now.")
        finally:
            os.remove(file_path)
    else:
        await update.message.reply_text("📂 Please upload an image file after typing /convert.")

# /feedback
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if text:
        with open("feedback.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
        await update.message.reply_text("✅ Thanks for your feedback!")
    else:
        await update.message.reply_text("📝 Please type your feedback after /feedback.")

# /fun
async def fun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 Why don’t skeletons fight each other? Because they don’t have the guts!",
        "🤣 Parallel lines have so much in common. Too bad they’ll never meet.",
        "😆 I told my computer I needed a break, and it said: 'No problem, I’ll go to sleep.'"
    ]
    await update.message.reply_text(random.choice(jokes))

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(CommandHandler("fun", fun))
    app.add_handler(MessageHandler(filters.Document.ALL, convert))  # for file upload

    app.run_polling()

if __name__ == "__main__":
    main()
