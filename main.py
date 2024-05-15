import asyncio
import logging
import sys
from datetime import datetime
from os import getenv
from typing import Iterable

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Filter
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv
from redis_dict import RedisDict

database = RedisDict('users')
load_dotenv()
TOKEN = getenv("BOT_TOKEN")
ADMIN_LIST = 1259522136,
dp = Dispatcher()


class IsAdmin(Filter):
    def __init__(self, admin_list: Iterable[int]) -> None:
        self.admin_list = admin_list

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_list


@dp.message(F.text.startswith("/stat"), IsAdmin(ADMIN_LIST))
async def stat(message: Message):
    users = database.get('users')
    user = message.text.split()[-1]
    for i in users.items():
        if i[0] == user:
            await message.answer(f"{i[1]}")
            return
    await message.answer("this user is not registered")
    database['users'] = users

@dp.message(IsAdmin(ADMIN_LIST), F.text.startswith("/send"))
async def send(message: Message, bot: Bot):
    user_id = message.text.split()[1]
    msg = message.text.split()[-1]
    await bot.send_message(text=msg, chat_id=user_id)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    users = database.get('users')
    user_id = str(message.from_user.id)
    users[user_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S"[: -3])
    database['users'] = users
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!\nYou are now registered")


async def on_startup(bot: Bot) -> None:
    database['users'] = database.get('users', {})
    command_list = [
        BotCommand(command='start', description='to start the bot')
    ]
    await bot.set_my_commands(command_list)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
