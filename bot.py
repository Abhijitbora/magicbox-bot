import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
from pydub import AudioSegment
from PIL import Image
import requests
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation handler
FEEDBACK = range(1)

# Start command
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🎵 Music Sharing", callback_data='music')],
        [InlineKeyboardButton("🔄 File Conversion", callback_data='convert')],
        [InlineKeyboardButton("📝 Feedback", callback_data='feedback')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Welcome to Multi-Function Bot! Choose an option:',
        reply_markup=reply_markup
    )

# Button handler
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data == 'music':
        query.edit_message_text(text="🎵 Send me an audio file and I'll help you share it with proper metadata")
    elif query.data == 'convert':
        query.edit_message_text(text="🔄 Send me a file and I'll convert it to your desired format")
    elif query.data == 'feedback':
        query.edit_message_text(text="📝 Please send your feedback. We appreciate it!")
        return FEEDBACK

# Music sharing function
def handle_audio(update: Update, context: CallbackContext) -> None:
    try:
        file = update.message.audio.get_file()
        file.download('input_audio.mp3')
        
        # Process audio metadata
        audio = AudioSegment.from_mp3("input_audio.mp3")
        # Add your metadata processing here
        
        update.message.reply_audio(audio=open('input_audio.mp3', 'rb'), 
                                  title="Processed Audio",
                                  performer="Music Bot")
        
        # Clean up
        os.remove('input_audio.mp3')
    except Exception as e:
        update.message.reply_text(f"Error processing audio: {str(e)}")

# File conversion function
def handle_document(update: Update, context: CallbackContext) -> None:
    try:
        document = update.message.document
        file_name = document.file_name.lower()
        
        if file_name.endswith('.pdf'):
            update.message.reply_text("PDF conversion selected")
            # Add PDF to image conversion logic here
            
        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            update.message.reply_text("Image conversion selected")
            # Add image conversion logic here
            
        else:
            update.message.reply_text("Unsupported file format for conversion")
            
    except Exception as e:
        update.message.reply_text(f"Error converting file: {str(e)}")

# Feedback conversation handler
def feedback(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please send us your feedback. Type /cancel to abort.")
    return FEEDBACK

def receive_feedback(update: Update, context: CallbackContext) -> int:
    user_feedback = update.message.text
    user = update.message.from_user
    
    # Send feedback to admin (you)
    context.bot.send_message(
        chat_id=os.environ.get('ADMIN_ID'), 
        text=f"📝 Feedback from {user.first_name}: {user_feedback}"
    )
    
    update.message.reply_text("Thank you for your feedback!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Feedback cancelled.')
    return ConversationHandler.END

# Error handler
def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function
def main() -> None:
    # Get the token from environment variable
    token = os.environ.get('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Add conversation handler for feedback
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^feedback$')],
        states={
            FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, receive_feedback)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_handler(MessageHandler(Filters.audio, handle_audio))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    
    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
