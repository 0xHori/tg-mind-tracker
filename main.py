import asyncio
import logging
import sys
from os import getenv
import aiosqlite


from dotenv import load_dotenv


from aiogram import Bot, Dispatcher, Router, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


load_dotenv()
TOKEN = getenv("BOT_TOKEN")



async def init_db():
    async with aiosqlite.connect("mood_tracker.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE
            )""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mini_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )""")
        await db.commit()
    








dp = Dispatcher(storage=MemoryStorage())

class MiniTask(StatesGroup):
    task = State()
    new_task = State()


minitask_router = Router()


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    db = await aiosqlite.connect("mood_tracker.db")
    await db.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (message.from_user.id,))
    await db.commit()
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я трекер настроения." \
                         "\nДоступные команды:" \
                         "\n/start - познакомлюсь с тобой" \
                         "\n/morning - Утренняя мотивация" \
                         "\n/day - Промежуточный этап" \
                         "\n/evening - спрошу про дела, как настроение")


@dp.message(Command("morning"))
async def command_morning(message: Message) -> None:
    await message.answer("Привет! Проговори 3 фразы спокойного себя:")
    await message.answer("Сейчас будет трудно. Это нормально." \
                         "\nМаленький шаг вперед важнее, чем быстрый результат." \
                         "\nКаждая ошибка — это опыт, а не доказательство слабости.")
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Готово", callback_data="ready"))
    await message.answer("Когда будешь готов, нажми кнопку 'Готово'", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "ready")
async def process_ready(callback: types.CallbackQuery):
    await callback.message.answer("Молодец!")
    await callback.answer()







@minitask_router.message(Command("day"))
async def command_day(message: Message, state: FSMContext) -> None:
    await message.answer("Какой мини-шаг ты сегодня делаешь?")
    await state.set_state(MiniTask.task)


@minitask_router.message(MiniTask.task)
async def process_task(message: Message, state: FSMContext):
    await state.update_data(task=message.text)
    db = await aiosqlite.connect("mood_tracker.db")
    await db.execute("INSERT INTO mini_tasks (user_id, task, date) VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?, date('now'))", (message.from_user.id, message.text))
    await db.commit()
    data = await state.get_data()
    await message.answer(f"Твой мини-шаг на сегодня: {data['task']}. Есть ещё какие-то мини-шаги, которые ты бы хотел сделать сегодня? Если да, то напиши их. Если нет, то напиши 'Нет'.")
    await state.set_state(MiniTask.new_task)

@minitask_router.message(MiniTask.new_task)
async def process_new_task(message: Message, state: FSMContext):
    await state.update_data(new_data=message.text)
    data = await state.get_data()
    if data['new_data'].lower() == 'нет':
        await message.answer("Хорошо, записал. Удачи тебе сегодня!")
        await state.clear()
        # нужен старт CRON
    else:
        db = await aiosqlite.connect("mood_tracker.db")
        await db.execute("INSERT INTO mini_tasks (user_id, task, date) VALUES ((SELECT id FROM users WHERE telegram_id = ?), ?, date('now'))", (message.from_user.id, message.text))
        await db.commit()
        await message.answer("Твой мини-шаг записан. Есть что-то ещё?")
        await state.set_state(MiniTask.new_task)




@dp.message(Command("evening"))
async def command_evening(message: Message) -> None:
    await message.answer("Что сделал? Какие эмоции?")
    # Нужно обработать по-другому.

    '''
    Что сделал сегодня?
    - Позанимался программированием
    Какие эмоции испытал сегодня?
    - Доволен собой, гордость, радость
    Хорошо, записал. Что-то ещё? | (btn:Да; btn:Нет, это всё )
    '''

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(minitask_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init_db())
    asyncio.run(main())
          