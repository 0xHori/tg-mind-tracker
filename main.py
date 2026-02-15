import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я трекер настроения." \
                         "\nДоступные команды:" \
                         "\n/start - познакомлюсь с тобой" \
                         "\n/morning - Утренняя мотивация" \
                         "\n/day - Промежуточный этап" \
                         "\n/evening - спрошу про дела, как настроение")


@dp.message(Command("morning"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Проговори 3 фразы спокойного себя:")
    await message.answer("Сейчас будет трудно. Это нормально." \
                         "\nМаленький шаг вперед важнее, чем быстрый результат." \
                         "\nКаждая ошибка — это опыт, а не доказательство слабости.")
    # Под сообщением должна быть кнопка "готово".
    # При нажатии на кнопку "Готово" бот отправит заготовленное сообщение: "Молодец!"

@dp.message(Command("day"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Какой мини-шаг ты сегодня делаешь?")
    # Бот ожидает ввода сообщения
    # Бот сохраняет сообщение в базу данных
    # Отправляет сообщение со статусом 200

    # через 2-3 должен спросить (CRON) "Сделал?"
    # Если нет - бот присылает мотивационную фразу

@dp.message(Command("evening"))
async def command_start_handler(message: Message) -> None:
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
          