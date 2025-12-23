"""
Основной файл Telegram бота для отслеживания криптокошельков
"""
import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from handlers import router
from services.notifications import monitor_wallets

# Настройка логирования
log_level = getattr(logging, config.log_level.upper(), logging.INFO)
os.makedirs(config.log_dir, exist_ok=True)
log_file = os.path.join(config.log_dir, "bot.log")
handlers = [
    logging.StreamHandler(),
    RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3),
]
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers,
)
logger = logging.getLogger(__name__)

notification_task: asyncio.Task | None = None


async def on_startup(bot: Bot):
    global notification_task
    notification_task = asyncio.create_task(
        monitor_wallets(bot, config.notify_interval_seconds)
    )


async def on_shutdown(bot: Bot):
    if notification_task:
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            pass

async def main():
    """Основная функция запуска бота"""
    # Проверка конфигурации
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        logger.error("Создайте файл .env на основе .env.example и укажите BOT_TOKEN")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    dp.include_router(router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("🚀 Бот запущен!")
    logger.info("Нажмите Ctrl+C для остановки")
    
    try:
        # Запуск polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()
        logger.info("👋 Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал остановки")
