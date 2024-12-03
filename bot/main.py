import asyncio
import logging
from logging import getLogger
from aiogram import Bot, Dispatcher


from bot.routes.start import start_router
from bot.routes.product_selection import category_slider
from config import settings

log = getLogger("mitm")


def get_bot() -> Bot:
    return Bot(token=settings.TOKEN)


async def main():
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(category_slider)

    log.info("Starting bot...")

    await dp.start_polling(get_bot())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
