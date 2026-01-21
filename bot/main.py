import asyncio
from aiogram import Bot, Dispatcher
from .logger_conf import logger
from .db.session import init_db
from .handlers import start
from .config import BOT_TOKEN
from .handlers import start, drink, stats, undo, top, beer


async def main():
    logger.info("Starting beerStat_bot 🍺")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(drink.router)
    dp.include_router(stats.router)
    dp.include_router(undo.router)
    dp.include_router(top.router)
    dp.include_router(beer.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
