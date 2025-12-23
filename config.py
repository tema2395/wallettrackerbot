"""
Конфигурация бота для загрузки переменных окружения
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass
class Config:
    """Класс конфигурации бота"""
    bot_token: str
    etherscan_api_key: str | None
    bscscan_api_key: str | None
    notify_interval_seconds: int
    cache_ttl_seconds: int
    rate_limit_min_interval: float
    log_dir: str
    log_level: str
    
    @classmethod
    def from_env(cls):
        """Загрузка конфигурации из переменных окружения"""
        return cls(
            bot_token=os.getenv('BOT_TOKEN', ''),
            etherscan_api_key=os.getenv('ETHERSCAN_API_KEY'),
            bscscan_api_key=os.getenv('BSCSCAN_API_KEY'),
            notify_interval_seconds=_get_int_env('NOTIFY_INTERVAL_SECONDS', 60),
            cache_ttl_seconds=_get_int_env('CACHE_TTL_SECONDS', 30),
            rate_limit_min_interval=_get_float_env('RATE_LIMIT_MIN_INTERVAL', 0.25),
            log_dir=os.getenv('LOG_DIR', 'logs'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )
    
    def validate(self):
        """Проверка обязательных параметров"""
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        return True

# Глобальный экземпляр конфигурации
config = Config.from_env()
