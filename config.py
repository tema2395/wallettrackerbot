"""
Конфигурация бота для загрузки переменных окружения
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    """Класс конфигурации бота"""
    bot_token: str
    etherscan_api_key: str | None
    bscscan_api_key: str | None
    
    @classmethod
    def from_env(cls):
        """Загрузка конфигурации из переменных окружения"""
        return cls(
            bot_token=os.getenv('BOT_TOKEN', ''),
            etherscan_api_key=os.getenv('ETHERSCAN_API_KEY'),
            bscscan_api_key=os.getenv('BSCSCAN_API_KEY'),
        )
    
    def validate(self):
        """Проверка обязательных параметров"""
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        return True

# Глобальный экземпляр конфигурации
config = Config.from_env()
