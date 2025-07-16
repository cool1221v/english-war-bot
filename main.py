
import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
import random
from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- DATABASE SETUP ---
conn = sqlite3.connect('main.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    nickname TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    rank TEXT DEFAULT 'Beginner',
    bronze INTEGER DEFAULT 0,
    silver INTEGER DEFAULT 0,
    gold INTEGER DEFAULT 0,
    diamond INTEGER DEFAULT 0,
    gem INTEGER DEFAULT 0
)''')
conn.commit()

# --- COMMAND HANDLERS ---

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone():
        await message.answer("You're already registered.")
    else:
        await message.answer("Welcome! What nickname do you want to use?")
        @dp.message_handler()
        async def get_nickname(msg: types.Message):
            nickname = msg.text.strip()
            cursor.execute("INSERT INTO users (id, username, nickname) VALUES (?, ?, ?)",
                           (user_id, msg.from_user.username, nickname))
            conn.commit()
            await msg.answer(f"Nickname set! Welcome to the grind, {nickname}. Use /quiz to begin.")
        return

@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT nickname, xp, level, rank, bronze, silver, gold, diamond, gem FROM users WHERE id = ?",
                   (user_id,))
    data = cursor.fetchone()
    if data:
        nickname, xp, level, rank, bronze, silver, gold, diamond, gem = data
        await message.answer(
            f"🪪 Nickname: {nickname}
🎯 Rank: {rank}
🧠 Level: {level}
📈 XP: {xp}

💰 Wallet:
🥉 Bronze: {bronze}
🥈 Silver: {silver}
🥇 Gold: {gold}
💎 Diamond: {diamond}
🔷 Gem: {gem}"
        )
    else:
        await message.answer("You are not registered. Use /start.")

@dp.message_handler(commands=['quiz'])
async def quiz(message: types.Message):
    questions = [
        {
            'q': "Which sentence is correct?",
            'options': ["She suggested to go.", "She suggested going.", "She suggested that to go.", "She suggested go."],
            'a': 1
        },
        {
            'q': "Rewrite: They didn’t tell me the truth. (honest)",
            'options': ["They were honesty.", "They weren’t honest with me.", "They are not honest.", "They told honestly."],
            'a': 1
        },
        {
            'q': "IELTS: Recycling rates have tripled since 1990. (T/F/NG)",
            'options': ["True", "False", "Not Given"],
            'a': 0
        }
    ]
    q = random.choice(questions)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for opt in q['options']:
        markup.add(opt)

    await message.answer(f"🧠 {q['q']}", reply_markup=markup)

    @dp.message_handler(lambda msg: msg.text in q['options'])
    async def answer_handler(msg: types.Message):
        idx = q['options'].index(msg.text)
        if idx == q['a']:
            cursor.execute("UPDATE users SET xp = xp + 50, bronze = bronze + 10 WHERE id = ?", (msg.from_user.id,))
            conn.commit()
            await msg.answer("✅ Correct! +50 XP, +10 Bronze")
        else:
            await msg.answer("❌ Wrong. Try again next time.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
