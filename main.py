import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from dotenv import load_dotenv

from config import database
from routers.information import information_router
from routers.registration import registration_router
from routers.start import start_router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import json
import logging
import os
import sys
from random import sample, shuffle
from time import sleep

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

WEB_SERVER_HOST = getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = int(getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = getenv("WEBHOOK_PATH")
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = getenv("BASE_WEBHOOK_URL")


async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
    database['users'] = database.get('users', {})

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)

def main() -> None:
    dp = Dispatcher()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    i18n = I18n(path="locales", default_locale="en", domain="messages")
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.startup.register(on_startup)
    dp.include_routers(start_router, information_router, registration_router)


    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
