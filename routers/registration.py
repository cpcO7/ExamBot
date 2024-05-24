from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import ADMIN_LIST, database
from main_keyboard import make_main_keyboard
from state import Register

registration_router = Router()


@registration_router.message(F.text == __('Registration'))
async def register(message: Message, state: FSMContext):
    rkm = ReplyKeyboardRemove()
    await state.set_state(Register.full_name)
    await message.answer(_('Please enter your full name: \nExample: Yozilov Shahriyor'), reply_markup=rkm)


@registration_router.message(Register.full_name)
async def register_user(message: Message, state: FSMContext):
    rkb = ReplyKeyboardBuilder()
    rkb.row(KeyboardButton(text='Phone Number', request_contact=True))
    await state.update_data(full_name=message.text)
    await state.set_state(Register.phone_number)
    await message.answer(
        _('Please click button to send your phone number or enter your phone number: \nExample: +998956012347'),
        reply_markup=rkb.as_markup(resize_keyboard=True))


@registration_router.message(Register.phone_number)
async def send_message(message: Message, state: FSMContext):
    rkm = ReplyKeyboardRemove()
    if message.content_type == 'contact':
        phone = '+' + message.contact.phone_number
    else:
        phone = message.text
    await state.update_data(phone_number=phone)
    await state.set_state(Register.email_address)
    await message.answer(_('Please enter your email: \nExample: helloworld@gmail.com'), reply_markup=rkm)


@registration_router.message(Register.email_address)
async def send_message(message: Message, state: FSMContext):
    await state.update_data(email_address=message.text)
    await state.set_state(Register.current_country_of_residence)
    await message.answer(_('Please enter your country:\nExample: England'))


@registration_router.message(Register.current_country_of_residence)
async def send_message(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    await state.update_data(current_country_of_residence=message.text)
    data = await state.get_data()
    await state.set_state(Register.nationality)
    await message.answer(_('Please enter your nationality:\nExample: English'))
    users = database['users']
    users[user_id] = {'user id': user_id, 'full name': data.get('full_name'), 'email': data.get('email_address'),
                      'country': data.get('current_country_of_residence'), 'phone': data.get('phone_number')}
    database['users'] = users


@registration_router.message(Register.nationality)
async def send_message(message: Message, state: FSMContext):
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text=_("🎓University student"), callback_data="student_University student"),
            InlineKeyboardButton(text=_("🎓Master's student"), callback_data="student_Master's student"),
            InlineKeyboardButton(text=_("🎓Bachelor's graduate"), callback_data="student_Bachelor's graduate"),
            InlineKeyboardButton(text=_("🎓Master's graduate"), callback_data="student_Master's graduate"),
            InlineKeyboardButton(text=_("🧪PhD scholar"), callback_data="student_PhD scholar"),
            InlineKeyboardButton(text=_("🥼Doctor of Science (DsC) scholar"),
                                 callback_data="student_Doctor of Science (DsC) scholar"),
            InlineKeyboardButton(text=_("👇 Other..."), callback_data="other"))
    ikb.adjust(2, repeat=True)

    await state.update_data(nationality=message.text)
    await state.set_state(Register.highest_degree_attained)
    await message.answer(_('Mark the highest level you have achieved: '), reply_markup=ikb.as_markup())

@registration_router.callback_query(F.data.startswith('student'))
async def student_callback_query(callback: CallbackQuery, state: FSMContext):
    status_student = callback.data.split('_')[1:]
    await callback.message.delete()
    await state.update_data(highest_degree_attained=status_student)
    await state.set_state(Register.name_of_institution)
    await callback.message.answer(_("<b>Enter your University name: </b>"))


@registration_router.callback_query(F.data == __('other'))
async def other_callback_query(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Register.highest_degree_attained)
    await callback.message.edit_text(
        _("<b>Enter your highest degree attained: </b>\n<em>For example: University student, Master's student, etc.</em>"))


@registration_router.message(Register.highest_degree_attained)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(highest_degree_attained=message.text)
    await state.set_state(Register.name_of_institution)
    await message.answer(_("<b>Enter the name of your university: </b>"))


@registration_router.message(Register.name_of_institution)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(name_of_institution=message.text)
    await state.set_state(Register.field_of_study)
    await message.answer(_("<b>Enter your field of study: </b>"))


@registration_router.message(Register.field_of_study)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(field_of_study=message.text)
    await state.set_state(Register.academic_achivements_or_awards)
    await message.answer(
        _("<b>If you have, enter your academic achivements or award, otherwise send as I don't have </b>"))


@registration_router.message(Register.academic_achivements_or_awards)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(academic_achivements_or_awards=message.text)
    await state.set_state(Register.current_job)
    await message.answer(_("<b>Enter your current job </b>"))


@registration_router.message(Register.current_job)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(current_job=message.text)
    await state.set_state(Register.current_workplace)
    await message.answer(_("<b>Enter your current workplace </b>"))


@registration_router.message(Register.current_workplace)
async def highest_degree_attained(message: Message, state: FSMContext):
    await state.update_data(current_workplace=message.text)
    data = await state.get_data()
    text = _(
        """ 
        <b>The form you filled out</b>
        Full name: {full_name}
        Email address: {email_address}
        Phone number: {phone_number}
        Nationality: {nationality}
        Current country of residence: {current_country_of_residence}
        Highest degree attained: {highest_degree_attained}
        University name: {name_of_institution}
        Field of study: {field_of_study}
        Academic achievements or awards: {academic_achivements_or_awards}
        Current job position: {current_job}
        Current workplace: {current_workplace}
        """
    ).format(
        full_name=data.get('full_name'),
        email_address=data.get('email_address'),
        phone_number=data.get('phone_number'),
        nationality=data.get('nationality'),
        current_country_of_residence=data.get('current_country_of_residence'),
        highest_degree_attained=data.get('highest_degree_attained'),
        name_of_institution=data.get('name_of_institution'),
        field_of_study=data.get('field_of_study'),
        academic_achivements_or_awards=data.get('academic_achivements_or_awards'),
        current_job=data.get('current_job'),
        current_workplace=data.get('current_workplace')
    )

    ikb = InlineKeyboardBuilder()
    await state.update_data(text=text)
    ikb.row(InlineKeyboardButton(text=_("Continue"), callback_data="continue"),
            InlineKeyboardButton(text=_('Send to admin'), callback_data="send_admin"))
    await message.answer(text, reply_markup=ikb.as_markup())


@registration_router.callback_query(F.data == __('send_admin'))
async def send_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    data = await state.get_data()
    text = data.get('text')
    await state.clear()
    for admin in ADMIN_LIST:
        await bot.send_message(chat_id=admin, text=text)
    await callback.message.answer(_('Successfully sent to admin'), reply_markup=make_main_keyboard())


@registration_router.callback_query(F.data == __('continue'))
async def continue_(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(Register.detailed_information)
    text = _('''
How do you think you can contribute to making the internship interesting? 
Tell us about your hobbies, unique interests, and qualities you bring to the table. 
Please keep your answer to 50 words or less.
''')
    await callback.message.answer(text)


@registration_router.message(Register.detailed_information)
async def detailed_information(message: Message, state: FSMContext):
    await state.update_data(detailed_information=message.text)
    await state.set_state(Register.detailed_information1)
    await message.answer(
        _("What skills and knowledge do you hope to improve gain from this experience?\nPlease keep your answer to 50 words or less."))


@registration_router.message(Register.detailed_information1)
async def detailed_information1(message: Message, state: FSMContext):
    await state.update_data(detailed_information1=message.text)
    await state.set_state(Register.detailed_information2)
    await message.answer(_("How or where did you hear about this internship opportunity?"))


@registration_router.message(Register.detailed_information2)
async def detailed_information2(message: Message, state: FSMContext):
    await state.update_data(detailed_information2=message.text)
    await state.set_state(Register.detailed_information3)
    await message.answer(
        _("Is there any additional information you would like to share about yourself or your application?"))


@registration_router.message(Register.detailed_information3)
async def detailed_information3(message: Message, state: FSMContext):
    await state.update_data(detailed_information3=message.text)
    await state.set_state(Register.detailed_information4)
    await message.answer(_("Upload your CV/resume"))


@registration_router.message(Register.detailed_information4)
async def detailed_information4(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(detailed_information4=message.document.file_id)
    for admin in ADMIN_LIST:
        await bot.forward_message(chat_id=admin, from_chat_id=message.from_user.id, message_id=message.message_id,
                                  message_thread_id=message.message_thread_id)
    await state.set_state(Register.detailed_information5)
    await message.answer(_("Upload the cover letter in PDF format."))

@registration_router.message(Register.detailed_information5)
async def detailed_information(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(detailed_information5=message.document.file_id)
    for admin in ADMIN_LIST:
        await bot.forward_message(chat_id=admin, from_chat_id=message.from_user.id, message_id=message.message_id,
                                  message_thread_id=message.message_thread_id)
    data = await state.get_data()
    text = _(""" 
<b>The remaining part of the form you filled 👇</b>
{detailed_information}
{detailed_information1}
{detailed_information2}
{detailed_information3}
""").format(
        detailed_information=data.get('detailed_information'),
        detailed_information1=data.get('detailed_information1'),
        detailed_information2=data.get('detailed_information2'),
        detailed_information3=data.get('detailed_information3')
    )

    await message.answer(text)
    for admin in ADMIN_LIST:
        await bot.send_message(chat_id=admin, text=text)

