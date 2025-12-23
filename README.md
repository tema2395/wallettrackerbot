# Wallet Tracker Bot

Telegram бот для отслеживания криптокошельков с поддержкой TON, Ethereum и Binance Smart Chain.

## Возможности

- Просмотр баланса кошельков
- Последние 5 транзакций
- Поддержка TON, ETH, BSC
- Автоматическое определение типа блокчейна
- Форматирование данных
- Уведомления о новых транзакциях
- Кэширование и ограничение частоты запросов
- Ссылки на блокчейн-эксплореры
- Простой интерфейс

## Требования

- Python 3.11+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- (Опционально) API ключи для Etherscan и BscScan

## Установка

### Вариант 1: Локальная установка

1. **Клонируйте репозиторий:**
```bash
git clone <your-repo-url>
cd wallet-tracker-bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте конфигурацию:**
```bash
cp .env.example .env
nano .env  # или используйте любой текстовый редактор
```

Заполните `.env` файл:
```env
BOT_TOKEN=your_telegram_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key  # опционально
BSCSCAN_API_KEY=your_bscscan_api_key      # опционально
NOTIFY_INTERVAL_SECONDS=60               # опционально
CACHE_TTL_SECONDS=30                      # опционально
RATE_LIMIT_MIN_INTERVAL=0.25             # опционально
LOG_DIR=logs                              # опционально
LOG_LEVEL=INFO                            # опционально
```

5. **Запустите бота:**
```bash
python bot.py
```

### Вариант 2: Docker

1. **Создайте `.env` файл:**
```bash
cp .env.example .env
nano .env
```

2. **Запустите через Docker Compose:**
```bash
docker-compose up -d
```

3. **Просмотр логов:**
```bash
docker-compose logs -f
```

4. **Остановка:**
```bash
docker-compose down
```

## Получение API ключей

### Telegram Bot Token

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### Etherscan API Key (опционально)

1. Зарегистрируйтесь на [etherscan.io](https://etherscan.io/register)
2. Перейдите в [API Keys](https://etherscan.io/myapikey)
3. Создайте новый ключ

### BscScan API Key (опционально)

1. Зарегистрируйтесь на [bscscan.com](https://bscscan.com/register)
2. Перейдите в [API Keys](https://bscscan.com/myapikey)
3. Создайте новый ключ

**Примечание:** API ключи для Etherscan и BscScan необязательны. Бот будет работать и без них, но с ограничениями по количеству запросов.

## Использование

### Команды бота

- `/start` - Начало работы с ботом
- `/track` - Отследить кошелек
- `/list` - Список отслеживаемых кошельков
- `/untrack` - Удалить кошелек из отслеживания
- `/help` - Справка по использованию

### Примеры адресов

**TON:**
```
EQD1Lp1KcmGHFpE8eIvL1mnHT83b4HdB8HJxuSfq6Rq4zGyN
```

**Ethereum:**
```
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**BSC:**
```
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### Как использовать

1. Отправьте боту команду `/track` или просто адрес кошелька
2. Если адрес может быть ETH или BSC, выберите нужную сеть
3. Получите информацию о балансе, транзакциях и уведомлениях

## Структура проекта

```
wallet-tracker-bot/
├── bot.py                      # Основной файл бота
├── config.py                   # Конфигурация
├── requirements.txt            # Зависимости
├── .env.example                # Пример конфигурации
├── Dockerfile                  # Docker образ
├── docker-compose.yml          # Docker Compose конфигурация
├── README.md                   # Документация
│
├── blockchain/                 # Модули для работы с блокчейнами
│   ├── __init__.py
│   ├── ton_tracker.py         # TON blockchain
│   ├── eth_tracker.py         # Ethereum blockchain
│   └── bsc_tracker.py         # BSC blockchain
│
├── handlers/                   # Обработчики команд
│   ├── __init__.py
│   └── wallet_handlers.py     # Обработчики кошельков
│
├── services/                   # Сервисные модули
│   ├── __init__.py
│   ├── notifications.py       # Уведомления о новых транзакциях
│   └── trackers.py            # Инициализация трекеров
│
└── utils/                      # Утилиты
    ├── __init__.py
    ├── formatters.py          # Форматирование данных
    ├── network.py             # Кэширование и ограничение запросов
    └── validators.py          # Валидация адресов
```

## Технологии

- **aiogram 3.4.1** - Асинхронный фреймворк для Telegram ботов
- **aiohttp** - Асинхронные HTTP запросы
- **python-dotenv** - Управление переменными окружения
- **pydantic** - Валидация данных

## Используемые API

- [Tonscan API](https://toncenter.com/api/v2/) - для TON
- [Etherscan API](https://docs.etherscan.io/) - для Ethereum
- [BscScan API](https://docs.bscscan.com/) - для BSC

## Особенности реализации

### Автоматическое определение блокчейна

Бот автоматически определяет тип блокчейна по формату адреса:
- TON: адреса из 48 символов, начинающиеся с `EQ` или `UQ`
- ETH/BSC: адреса из 42 символов, начинающиеся с `0x`

### Обработка транзакций

- Показываются последние 5 транзакций
- Различается тип (входящие/исходящие)
- Форматирование дат и сумм
- Сокращение длинных адресов и хешей

### Уведомления

- Автоматическая подписка на кошелек при запросе
- Периодическая проверка новых транзакций
- Уведомления отправляются в чат пользователя

### Ссылки на эксплореры

Для каждого кошелька предоставляется прямая ссылка на соответствующий блокчейн-эксплорер:
- TON: [tonscan.org](https://tonscan.org)
- ETH: [etherscan.io](https://etherscan.io)
- BSC: [bscscan.com](https://bscscan.com)

## Решение проблем

### Бот не отвечает

1. Проверьте токен в `.env` файле
2. Убедитесь, что бот запущен
3. Проверьте логи: `docker-compose logs -f` или вывод в терминале

### Ошибки при получении данных

1. Проверьте интернет-соединение
2. API блокчейнов могут быть временно недоступны
3. Проверьте правильность адреса кошелька

### Лимиты API

Без API ключей есть ограничения:
- Etherscan: 5 запросов в секунду
- BscScan: 5 запросов в секунду

Получите API ключи для увеличения лимитов.

## Расширения

Бот можно легко расширить:

- Добавить поддержку других блокчейнов
- Сохранение избранных кошельков
- Отслеживание токенов (ERC-20, BEP-20)
- Статистика и графики
- Multi-wallet отслеживание

## Лицензия

MIT License


## Вклад

Приветствуются pull requests и issues!

---

Спасибо за использование.
