from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sending a message to the chat with the chat_id
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Chat ID is: {update.effective_chat.id}")

if __name__ == '__main__':
    # Replace 'YOUR_TOKEN_HERE' with your bot's token
    application = Application.builder().token('YOUR_TOKEN_HERE').build()

    # Adds the /start command handler
    application.add_handler(CommandHandler('start', start))

    # Starts polling updates from Telegram
    application.run_polling()


#run this the send /start to the bot