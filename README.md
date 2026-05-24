# Isekai Tracker 🗡️

**Isekai Tracker** is a gamified, automated fitness tracking application that turns your real-life daily steps into an epic Isekai light novel adventure. With every step you take, your character levels up, discovers new items, and progresses through an immersive story uniquely generated for you.

## 🌟 Features

- **RPG Progression & Unlocks**: Converts real-world activity into RPG progression: Gain EXP, level-ups, HP/Mana stats, world region unlocks(explore new biomes), encounter enemies, and document your milestones in the Adventure Log.
- **Automated Story Generation**: Integrated **Groq (Llama 3) LLM** and **Hugging Face (FLUX.1)** image model via background cron jobs to auto-generate personalized daily narrative Isekai story chapters based on your fitness activity with AI-illustrated scenes hosted on **Cloudinary**. Walk more, and your story progresses faster!
- **Loot Drop System**: Implemented a loot drop system with tiered rarity (Common to Legendary), an equippable inventory with stat bonuses (EXP multipliers, HP/Mana buffs), and Epic/Legendary loot email alerts via Brevo transactional API.
- **Google Fit Integration**: Automatically syncs your daily steps and distance traveled.
- **Daily Cron Automation**: Reliable daily story generation and step syncing without manual intervention.

## 🛠️ Tech Stack

### Backend
- **Python & Django (6.0)**: Core web framework and database ORM.
- **PostgreSQL**: Production database.
- **Google Cloud APIs**: For Google OAuth and Google Fit data retrieval.
- **Celery / Cron Job**: For executing automated tasks securely.
- **Brevo API**: For sending Epic/Legendary loot transactional email alerts.

### AI & Media Pipelines
- **Groq (Llama 3) LLM**: Auto-generates personalized daily Isekai story chapters.
- **Hugging Face (FLUX.1)**: Image model for generating AI-illustrated scenes.
- **Cloudinary**: Cloud storage and CDN for hosting generated images.

### Frontend
- **HTML & Django Templates**: Backend-rendered pages.
- **Tailwind CSS v4**: Utility-first styling for a sleek, responsive interface.

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js (for Tailwind CSS)
- A Google Cloud Console project with the Fit API enabled.
- API Keys for: Groq, Hugging Face, Cloudinary, and potentially Brevo (for email notifications).

### Local Environment Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/KaushikBarnwal/Isekai_Tracker.git
   cd Isekai_Tracker
   ```

2. **Set up Python Virtual Environment:**
   ```bash
   python -m venv env
   env\Scripts\activate  # On iOS: source env/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and populate it with:
   ```env
   # Django Secrets
   CRON_SECRET_KEY=your_cron_secret_key
   DEBUG=True

   # APIs
   GROQ_API_KEY=your_groq_key
   HUGGINGFACE_API_KEY=your_hf_key
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_SECRET=your_cloudinary_secret_key
   CLOUDINARY_API_KEY=your_cloudinary_key
   BREVO_API_KEY=your_brevo_key

   # Google Fit Auth
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Servers:**
   You will need to run both the Django server and the Tailwind CSS watcher:
   ```bash
   # Terminal 1: Django
   python manage.py runserver

   # Terminal 2: Tailwind
   npm run build:css
   ```

## 🎮 How to Play

1. **Sign Up & Link Google Fit**: Authenticate with your Google account and grant Fit permissions by sync button.
2. **Define Your Avatar**: Set up your character's DNA, appearance, and starting gear.
3. **Walk!**: Go about your everyday routine.
4. **Read Your Story**: Check the app the next day (or trigger a sync) to read the new chapter of your adventure based on yesterday's step count, complete with AI-generated art!

## 📜 License

This project is licensed under the Apache License 2.0. See the `Apache License 2.0` file for details.
