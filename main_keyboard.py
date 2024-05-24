from aiogram.types import KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_main_keyboard(**kwargs):
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=_('Registration', **kwargs)), KeyboardButton(text=_('About us', **kwargs)),
            KeyboardButton(text=_('Change language', **kwargs)))
    rkb.adjust(2, repeat=True)
    return rkb.as_markup(resize_keyboard=True)
