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

├── 🗂️ alembic/            → Alembic migration scripts

├── 🖼️ media/              → Media assets (local, optional)

├── 🧬 migrations/         → Manual or custom migration logic

📁 src/

├── 🧩 components/                  # Core bot logic

│   ├── 🗺️ excursion/              # Excursion models and behavior

│   │   ├── 📄 excursion.py

│   │   ├── 📊 stats_object.py

│   │   └── 📍 point/              # Point and extra content

│   │       ├── 📄 information_part.py

│   │       └── 📄 point.py

│   │
│   ├── 🧾 field.py                 # Field logic for admin editing

│   ├── ✉️ messages/              # Bot message sending

│   │   ├── 👮 admin_message_sender.py

│   │   ├── 🤖 bot.py

│   │   └── 📬 message_sender.py

│   └── 👤 user/                   # User state and interaction

│       ├── 🛠️ user_editor.py

│       └── 👤 user_state.py
│
├── 📌 constants.py                # Shared constants (e.g. field names, emoji)

├── 📦 data/                       # Data helpers

│   ├── 🐘 postgres_data_loader.py  # PostgreSQL loader

│   └── ☁️ s3bucket.py             # AWS S3 interface

│
├── 🗃️ database/                   # DB schema and connection

│   ├── 🧬 models.py               # SQLAlchemy models

│   └── 🔌 session.py              # DB session setup

│
├── 🚀 main.py                     # Entry point for running the bot

└── ⚙️ settings.py                 # Environment/config (from `.env`)

├── 📜 Procfile            → Heroku process declaration (entry point)

├── README.md                  # 📖 Project overview

└── LICENSE.md                 # 📜 Custom license file

## 📄 License

This project is proprietary. All rights reserved. Please contact the author for licensing inquiries.
