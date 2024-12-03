import asyncio
import logging
from logging import getLogger
from aiogram import Bot, Dispatcher


from bot.routes.start import start_router
from config import settings

log = getLogger("mitm")


def get_bot() -> Bot:
    return Bot(token=settings.BOT_NAME)


async def main():
    dp = Dispatcher()
    dp.include_router(start_router)

    log.info("Starting bot...")

    await dp.start_polling(get_bot())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
