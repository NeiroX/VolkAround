from src.components.messages.bot import Bot
from src.settings import TOKEN

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")  # Replace with your bot token

    bot = Bot(TOKEN)
    bot.run()
