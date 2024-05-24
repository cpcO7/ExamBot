from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

information_router = Router()


@information_router.message(F.text == __('About us'))
async def about(message: Message):
    text = _("""
Applications for the Skills & Management Internship program are open!

Maharat Institute of Research and Management is pleased to announce a three-month internship program in the fields of Law, Education, Economics, Media, Journalism and Computer Science!

📝 Eligibility:
- University students, recent graduates and people wishing to enrich their knowledge through research work.
- Availability and commitment to a 3-month program
- Ability to work in Microsoft Office package
- Open to LLL (lifelong learning).
- Knowledge of English

💼Advantage:

- Participation in effective projects
- gaining valuable experience in research and project development
- Expand your connections and develop personally and professionally.
- Receive certificate and recommendations upon successful completion

📅 Deadline: June 7, 2024

✅ Form: click here.

📩 Apply now and become part of a dynamic community dedicated to human capital development in Uzbekistan and beyond.""")

    await message.answer(text)
