import pandas as pd
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, InlineKeyboardButton, CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import database
from main_keyboard import make_main_keyboard

start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer(_('Hello {first_name}, welcome to our bot!').format(first_name=message.from_user.first_name),
                         reply_markup=make_main_keyboard())


@start_router.message(Command(commands='exel'))
async def exel(message: Message):
    users = database.get('users')
    if users == {}:
        await message.answer(_('There are no users yet'))
    else:
        file_name = 'users.xlsx'
        pd.DataFrame(list(database.get('users').values())).to_excel(file_name)
        file = FSInputFile(file_name)
        await message.answer_document(file, caption=_('Users info'))


@start_router.message(F.text == __('Change language'))
async def change_lang(message: Message):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text=_('uzbek'), callback_data='lang_uz'),
            InlineKeyboardButton(text=_('english'), callback_data='lang_en'),
            InlineKeyboardButton(text=_('russian'), callback_data='lang_ru'))
    await message.answer(_('Choose the language'), reply_markup=ikb.as_markup())


@start_router.callback_query(F.data.startswith('lang'))
async def lang_callback(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split('_')[-1]
    await state.update_data(locale=lang_code)
    if lang_code == 'uz':
        lang = _('Uzbek', locale=lang_code)
    elif lang_code == 'en':
        lang = _('English', locale=lang_code)
    else:
        lang = _('Russian', locale=lang_code)
    await callback.answer(_('{lang} is selected', locale=lang_code).format(lang=lang))

    rkb = make_main_keyboard(locale=lang_code)
    msg = _('Welcome! Choose.', locale=lang_code)
    await callback.message.answer(text=msg, reply_markup=rkb)
