# VolkAround Bot 🤖

VolkAround is a Telegram bot built with Python that provides interactive experiences, excursions, and media-rich content to users. Designed with scalability and modularity in mind, the bot is deployed on **Heroku** and uses **Amazon S3** for efficient media storage.

## 🚀 Features

- 🗺️ Excursion points with audio, images, and descriptions
- 🧩 Dynamic quests and interactive elements
- 📍 Location-based content support
- ☁️ Amazon S3 integration for storing photos and audio
- 🗄️ PostgreSQL database (via Heroku add-on)
- 📦 Alembic for database migrations
- ⚙️ Hosted and running on Heroku

## 📁 Project Structure
VolkAround/
├── .venv/                  # Virtual environment
├── alembic/                # Alembic migration scripts
├── media/                  # Media assets (if stored locally)
├── migrations/             # Optional migration management
├── src/
│   ├── components/         # Core bot logic (points, parts)
│   ├── data/               # Optional data files
│   ├── database/           # DB models and engine
│   ├── constants.py        # Shared constants
│   ├── main.py             # Bot entry point
│   └── settings.py         # Environment/config handling
├── Procfile                # Heroku process declaration
├── requirements.txt        # Python dependencies
└── README.md               # You are here

## 📄 License

This project is proprietary. All rights reserved. Please contact the author for licensing inquiries.
