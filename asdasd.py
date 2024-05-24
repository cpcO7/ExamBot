import json
import logging
import os
import sys
from random import sample, shuffle
from time import sleep

from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.methods import SendPoll
from aiogram.types import KeyboardButton, InlineKeyboardButton, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv('../.env')

ADMIN = os.getenv("ADMIN")

TOKEN = os.getenv("BOT_TOKEN")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Unitlar'))
    kb.row(KeyboardButton(text='PDF'))
    with open('users.json') as file:
        read_file = json.load(file)
        read_file[str(message.from_user.id)] = {
            'firs_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'username': '@' + message.from_user.username
        }
        with open('users.json', 'w') as f:
            json.dump(read_file, f, indent=4)
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", parse_mode=ParseMode.HTML)
    await message.answer(f"Tanlang: ", reply_markup=kb.as_markup(resize_keyboard=True))
    await message.bot.send_message(ADMIN,
                                   f'id: {message.chat.id}, \nname: {message.from_user.full_name}, \nusername: @{message.from_user.username}')


@router.message(F.text == 'PDF')
async def advancing_pdf_handler(message: Message, bot: Bot):
    _file = FSInputFile('Advancing_Vocabulary_Skills.pdf')
    await message.answer('Iltimos biroz kuting...🙏')
    await bot.send_document(message.chat.id, _file)


@router.message(F.text == 'Unitlar')
async def quizz(message: Message) -> None:
    ib = InlineKeyboardBuilder()
    for i in range(1, 20, 3):
        ib.row(InlineKeyboardButton(text='Unit ' + str(i), callback_data='Unit_' + str(i)),
               InlineKeyboardButton(text='Unit ' + str(i + 1), callback_data='Unit_' + str(i + 1)),
               InlineKeyboardButton(text='Unit ' + str(i + 2), callback_data='Unit_' + str(i + 2)))
    await message.answer('Unitlardan birini tanlang', reply_markup=ib.as_markup())


@router.callback_query(F.data.startswith('Unit_'))
async def callback_query(callback: CallbackQuery, bot: Bot):
    sleep(0.3)
    try:
        with open('units/' + callback.data + '.txt', 'r') as file:
            ib = InlineKeyboardBuilder()
            ib.row(InlineKeyboardButton(text='Tarjimalari', callback_data='trans-' + callback.data))
            ib.row(InlineKeyboardButton(text='Quizz testni boshlash', callback_data='start-' + callback.data))
            ib.row(InlineKeyboardButton(text='Unit tanlash', callback_data='menu'))
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            await bot.send_message(callback.message.chat.id, 'Unit ' + callback.data.split('_')[1],
                                   reply_markup=ib.as_markup())
            # await bot.edit_message_text('Unit ' + callback.data.split('_')[1], callback.message.chatid,
            #                             callback.message.message_id,
            #                             reply_markup=ib.as_markup())
    except FileNotFoundError:
        await callback.answer('No vocabularies in this unit 😑', show_alert=True)


@router.callback_query(F.data.startswith('trans'))
async def callback_query_trans(callback: CallbackQuery, bot: Bot):
    sleep(0.3)
    with open('units/' + callback.data.split('-')[1] + '.txt', 'r') as file:
        read_file = file.readlines()
        ib = InlineKeyboardBuilder()
        ib.row(InlineKeyboardButton(text='Quizz testni boshlash', callback_data='start-' + callback.data.split('-')[1]))
        ib.row(InlineKeyboardButton(text='Unit tanlash', callback_data='menu'))
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await bot.send_message(callback.message.chat.id,
                               'Unit ' + callback.data.split('_')[1] + '\n\n' + ''.join(read_file),
                               reply_markup=ib.as_markup())
        # await bot.edit_message_text('Unit ' + callback.data.split('_')[1] + '\n\n' + ''.join(read_file),
        #                             callback.message.chat.id, callback.message.message_id,
        #                             reply_markup=ib.as_markup())


@router.callback_query(F.data == 'menu')
async def callback_query_menu(callback: CallbackQuery, bot: Bot):
    ib = InlineKeyboardBuilder()
    for i in range(1, 20, 3):
        ib.row(InlineKeyboardButton(text='Unit ' + str(i), callback_data='Unit_' + str(i)),
               InlineKeyboardButton(text='Unit ' + str(i + 1), callback_data='Unit_' + str(i + 1)),
               InlineKeyboardButton(text='Unit ' + str(i + 2), callback_data='Unit_' + str(i + 2)))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await bot.send_message(callback.message.chat.id, 'Unit tanlang: ', reply_markup=ib.as_markup())
    # await bot.edit_message_text('Unit tanlang: ', callback.message.chat.id,
    #                             callback.message.message_id,
    #                             reply_markup=ib.as_markup())


check = []
word_list = []


def choice_one(_list: list):
    if len(check) == 10:
        return None
    else:
        p = sample(_list, 1)
        if p not in check and p is not None:
            check.append(p)
            return p
        else:
            return choice_one(_list)


def choice_three(selected_qst, r_f: list) -> list[str]:
    qst3 = sample(r_f, 3)
    for i in qst3:
        if i == selected_qst:
            return choice_three(selected_qst, r_f)
    else:
        return qst3


back_name = ''

overall = {
    'words': [],
    'a': []
}


async def start_quiz(chat_id, bot: Bot, r_f: list):
    qst = choice_one(r_f)
    global back_name, overall
    if qst is None:
        ikb = InlineKeyboardBuilder()
        ikb.row(InlineKeyboardButton(text='Qayta test yechish', callback_data='start-' + back_name))
        kb = ReplyKeyboardBuilder()
        kb.row(KeyboardButton(text='Unitlar'))
        kb.row(KeyboardButton(text='PDF'))
        rrr = ''
        i = 0
        while i <= 9:
            # rrr += f'{overall['words'][i]}:  ' + ('✅' if not overall['a'][i + 1] else '❌') + '\n'
            rrr += overall['words'][i] + ': ' + ('✅' if overall['a'][i] == 1 else '❌') + '\n'
            i += 1
        await bot.send_message(chat_id, f"To'g'ri javoblar:\n{rrr}",
                               reply_markup=kb.as_markup(resize_keyboard=True))
        await bot.send_message(chat_id, 'Test tugadi', reply_markup=ikb.as_markup())
        global check, word_list
        check = []
        word_list = []
        back_name = ''
    else:
        qst3 = choice_three(qst[0], r_f)

        qst3.append(qst[0])
        qst3 = list(map(lambda x: x.split('-')[1], qst3))
        shuffle(qst3)
        question = qst[0].split('-')[0]
        answers = qst3

        if answers[0] == qst[0].split('-')[1]:
            correct_option_id = 0
        elif answers[1] == qst[0].split('-')[1]:
            correct_option_id = 1
        elif answers[2] == qst[0].split('-')[1]:
            correct_option_id = 2
        elif answers[3] == qst[0].split('-')[1]:
            correct_option_id = 3
        overall['words'].append(question)
        overall['a'].append(correct_option_id)
        await bot.send_poll(chat_id, question, options=answers, is_anonymous=False, type='quiz', open_period=20,
                            correct_option_id=correct_option_id)


@router.callback_query(F.data.startswith('start'))
async def callback_query_start(callback: CallbackQuery, bot: Bot):
    rm = ReplyKeyboardRemove()
    await bot.edit_message_text('3', callback.message.chat.id, callback.message.message_id)
    sleep(0.3)
    await bot.edit_message_text('2', callback.message.chat.id, callback.message.message_id)
    sleep(0.3)
    await bot.edit_message_text('1', callback.message.chat.id, callback.message.message_id)
    sleep(0.3)
    await bot.edit_message_text('..ketdik', callback.message.chat.id, callback.message.message_id)
    sleep(0.3)
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await bot.send_message(callback.message.chat.id, 'Unit' + ' ' + callback.data[-1], reply_markup=rm)
    # await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
    #                             text='Unit' + ' ' + callback.data[-1])
    global back_name
    back_name = callback.data.split('-')[-1]
    with open('units/' + callback.data.split('-')[1] + '.txt') as file:
        read_file = file.readlines()
        word_list.append(read_file)
        await start_quiz(callback.message.chat.id, bot, read_file)


@router.poll_answer()
async def poll_answer(poll: SendPoll, bot: Bot):
    await start_quiz(poll.user.id, bot, word_list[0])
    global overall
    # print(poll.option_ids[0])
    if poll.option_ids[0] == overall['a'][-2]:
        print(True)
    else:
        print(False)
    if len(overall['words']) == 11:
        overall = {
            'words': [],
            'a': []
        }


@router.callback_query(F.data == 'units')
async def unit_menu(message: Message):
    await quizz(message)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
