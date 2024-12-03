from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message


start_router = Router()


@start_router.message(Command("start"))
async def index(message: Message):
    user = message.from_user
