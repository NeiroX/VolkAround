from src.components.messages.bot import Bot
from src.constants import TOKEN

if __name__ == "__main__":

    # TODO: admin solution to edit existing excursions

    if not TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")  # Replace with your bot token

    bot = Bot(TOKEN)
    bot.run()
