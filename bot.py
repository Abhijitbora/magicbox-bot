import os
import random
import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 Welcome to MagicBox Bot!\n\n"
        "I can do:\n"
        "🎵 /music - Get a sample song\n"
        "📂 /convert - Convert an image to PNG\n"
        "📝 /feedback <your text> - Send feedback\n"
        "😂 /fun - Get a random joke\n"
        "🤝 /help - Show this message again"
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# /music command
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🎵 Here's a sample song for you!")
        await update.message.reply_audio(InputFile("sample.mp3"))
    except Exception as e:
        logger.error(f"Error in music command: {e}")
        await update.message.reply_text("⚠️ Sorry, I couldn't send the music file right now.")

# /convert command
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document or update.message.photo:
        try:
            if update.message.document:
                file = await update.message.document.get_file()
                file_name = update.message.document.file_name
            else:
                # Handle photo messages
                file = await update.message.photo[-1].get_file()
                file_name = "photo.jpg"
                
            file_path = f"temp_{file_name}"
            await file.download_to_drive(file_path)

            # Convert to PNG
            img = Image.open(file_path)
            png_path = file_path.rsplit(".", 1)[0] + ".png"
            img.save(png_path, "PNG")
            
            await update.message.reply_document(InputFile(png_path), caption="✅ Here's your converted image!")
            
            # Clean up
            os.remove(png_path)
            os.remove(file_path)
            
        except Exception as e:
            logger.error(f"Error in convert command: {e}")
            await update.message.reply_text("⚠️ Only image files can be converted right now.")
            # Clean up if files were created
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            if 'png_path' in locals() and os.path.exists(png_path):
                os.remove(png_path)
    else:
        await update.message.reply_text("📂 Please upload an image file or send it as a photo after typing /convert.")

# /feedback command
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if text:
        try:
            with open("feedback.txt", "a", encoding="utf-8") as f:
                f.write(f"User {update.effective_user.id}: {text}\n")
            await update.message.reply_text("✅ Thanks for your feedback!")
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            await update.message.reply_text("⚠️ Sorry, I couldn't save your feedback right now.")
    else:
        await update.message.reply_text("📝 Please type your feedback after /feedback. Example: /feedback This bot is great!")

# /fun command
async def fun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 Why don't skeletons fight each other? Because they don't have the guts!",
        "🤣 Parallel lines have so much in common. Too bad they'll never meet.",
        "😆 I told my computer I needed a break, and it said: 'No problem, I'll go to sleep.'",
        "😄 Why did the scarecrow win an award? Because he was outstanding in his field!",
        "😊 What do you call a fake noodle? An impasta!"
    ]
    await update.message.reply_text(random.choice(jokes))

# Main function
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("music", music))
    application.add_handler(CommandHandler("convert", convert))
    application.add_handler(CommandHandler("feedback", feedback))
    application.add_handler(CommandHandler("fun", fun))
    
    # Handle document messages for conversion
    application.add_handler(MessageHandler(filters.Document.IMAGE | filters.Document.ALL, convert))
    
    # Handle photo messages for conversion
    application.add_handler(MessageHandler(filters.PHOTO, convert))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    if os.getenv("RENDER"):
        # On Render, use webhook method
        port = int(os.environ.get('PORT', 5000))
        webhook_url = os.getenv("WEBHOOK_URL")
        
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TOKEN,
                webhook_url=f"{webhook_url}/{TOKEN}"
            )
        else:
            # Fallback to polling if webhook URL not set
            logger.info("WEBHOOK_URL not set, using polling instead")
            application.run_polling()
    else:
        # Local development - use polling
        logger.info("Running in development mode (polling)")
        application.run_polling()

if __name__ == "__main__":
    main()
