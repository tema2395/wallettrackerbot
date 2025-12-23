"""
Обработчики команд Telegram бота
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.trackers import ton_tracker, eth_tracker, bsc_tracker
from services.notifications import (
    add_tracked_wallet,
    list_tracked_wallets,
    remove_tracked_wallet,
)
from utils import format_wallet_info, detect_blockchain

router = Router()

# Состояния для FSM
class WalletStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_blockchain_choice = State()
    waiting_for_untrack_address = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 <b>Привет! Я бот для отслеживания криптокошельков</b>\n\n"
        "Я могу показать баланс и последние транзакции для кошельков:\n"
        "💎 TON\n"
        "⟠ Ethereum (ETH)\n"
        "🟡 Binance Smart Chain (BSC)\n\n"
        "<b>Команды:</b>\n"
        "/track - Отследить кошелек\n"
        "/list - Список отслеживаемых кошельков\n"
        "/untrack - Удалить кошелек из отслеживания\n"
        "/help - Помощь\n\n"
        "Просто отправь мне адрес кошелька, и я покажу всю информацию!"
    )
    await message.answer(welcome_text, parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📖 <b>Справка по использованию</b>\n\n"
        "<b>Поддерживаемые блокчейны:</b>\n"
        "• TON - адреса начинаются с EQ или UQ (48 символов)\n"
        "• Ethereum - адреса начинаются с 0x (42 символа)\n"
        "• BSC - адреса начинаются с 0x (42 символа)\n\n"
        "<b>Как использовать:</b>\n"
        "1. Используй команду /track\n"
        "2. Отправь адрес кошелька\n"
        "3. Выбери блокчейн (если нужно)\n"
        "4. Получи информацию и уведомления о новых транзакциях\n\n"
        "<b>Дополнительные команды:</b>\n"
        "/list - Список отслеживаемых кошельков\n"
        "/untrack - Удалить кошелек из отслеживания\n\n"
        "<b>Примеры адресов:</b>\n"
        "TON: <code>EQD...xyz</code>\n"
        "ETH: <code>0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb</code>\n"
        "BSC: <code>0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb</code>\n\n"
        "💡 Бот автоматически определит тип кошелька по адресу!"
    )
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("track"))
async def cmd_track(message: Message, state: FSMContext):
    """Обработчик команды /track"""
    await message.answer(
        "📝 Отправь мне адрес кошелька, который хочешь отследить. "
        "Я включу уведомления о новых транзакциях.",
        parse_mode="HTML"
    )
    await state.set_state(WalletStates.waiting_for_address)


@router.message(Command("list"))
async def cmd_list(message: Message):
    """Список отслеживаемых кошельков"""
    wallets = list_tracked_wallets(message.chat.id)
    if not wallets:
        await message.answer("Список отслеживаемых кошельков пуст.", parse_mode="HTML")
        return

    lines = ["<b>Отслеживаемые кошельки:</b>"]
    for wallet in wallets:
        short_address = f"{wallet.address[:8]}...{wallet.address[-6:]}"
        lines.append(f"• {wallet.blockchain}: <code>{short_address}</code>")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("untrack"))
async def cmd_untrack(message: Message, state: FSMContext):
    """Удаление кошелька из отслеживания"""
    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        address = parts[1].strip()
        removed = await remove_tracked_wallet(message.chat.id, address)
        if removed:
            await message.answer("Кошелек удален из отслеживания.", parse_mode="HTML")
        else:
            await message.answer("Кошелек не найден в списке отслеживания.", parse_mode="HTML")
        return

    await message.answer(
        "Отправь адрес кошелька, который нужно удалить из отслеживания:",
        parse_mode="HTML",
    )
    await state.set_state(WalletStates.waiting_for_untrack_address)

@router.message(WalletStates.waiting_for_address)
async def process_wallet_address(message: Message, state: FSMContext):
    """Обработка введенного адреса кошелька"""
    address = message.text.strip()
    
    # Определяем тип блокчейна
    blockchain = detect_blockchain(address)
    
    if blockchain == 'UNKNOWN':
        await message.answer(
            "❌ Неверный формат адреса!\n\n"
            "Поддерживаемые форматы:\n"
            "• TON: EQ... или UQ... (48 символов)\n"
            "• ETH/BSC: 0x... (42 символа)\n\n"
            "Попробуй еще раз:",
            parse_mode="HTML"
        )
        return
    
    # Если адрес похож на ETH/BSC, предлагаем выбрать сеть
    if blockchain == 'ETH' and address.startswith('0x'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⟠ Ethereum", callback_data=f"track_eth_{address}"),
                InlineKeyboardButton(text="🟡 BSC", callback_data=f"track_bsc_{address}")
            ]
        ])
        await message.answer(
            "🤔 Этот адрес может быть как Ethereum, так и BSC.\n"
            "Выбери сеть:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Если это TON, сразу обрабатываем
    await state.clear()
    await process_ton_wallet(message, address)


@router.message(WalletStates.waiting_for_untrack_address)
async def process_untrack_address(message: Message, state: FSMContext):
    """Обработка адреса для удаления из отслеживания"""
    address = message.text.strip()
    removed = await remove_tracked_wallet(message.chat.id, address)
    if removed:
        await message.answer("Кошелек удален из отслеживания.", parse_mode="HTML")
    else:
        await message.answer("Кошелек не найден в списке отслеживания.", parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data.startswith("track_"))
async def process_blockchain_choice(callback: CallbackQuery):
    """Обработка выбора блокчейна"""
    data_parts = callback.data.split("_", 2)
    blockchain = data_parts[1]
    address = data_parts[2]
    
    await callback.message.edit_text("⏳ Загружаю данные...")
    
    if blockchain == "eth":
        await process_eth_wallet(callback.message, address)
    elif blockchain == "bsc":
        await process_bsc_wallet(callback.message, address)
    
    await callback.answer()

async def process_ton_wallet(message: Message, address: str):
    """Обработка TON кошелька"""
    status_msg = await message.answer("⏳ Загружаю данные TON кошелька...")
    
    # Получаем данные
    balance_data = await ton_tracker.get_balance(address)
    transactions = await ton_tracker.get_transactions(address, limit=5)
    explorer_link = ton_tracker.get_explorer_link(address)
    
    # Форматируем и отправляем
    wallet_info = format_wallet_info(
        address=address,
        blockchain='TON',
        balance_data=balance_data,
        transactions=transactions,
        explorer_link=explorer_link
    )
    
    await status_msg.edit_text(wallet_info, parse_mode="HTML", disable_web_page_preview=True)
    await _register_wallet(message, address, "TON")

async def process_eth_wallet(message: Message, address: str):
    """Обработка Ethereum кошелька"""
    # Получаем данные
    balance_data = await eth_tracker.get_balance(address)
    transactions = await eth_tracker.get_transactions(address, limit=5)
    explorer_link = eth_tracker.get_explorer_link(address)
    
    # Форматируем и отправляем
    wallet_info = format_wallet_info(
        address=address,
        blockchain='ETH',
        balance_data=balance_data,
        transactions=transactions,
        explorer_link=explorer_link
    )
    
    await message.answer(wallet_info, parse_mode="HTML", disable_web_page_preview=True)
    await _register_wallet(message, address, "ETH")

async def process_bsc_wallet(message: Message, address: str):
    """Обработка BSC кошелька"""
    # Получаем данные
    balance_data = await bsc_tracker.get_balance(address)
    transactions = await bsc_tracker.get_transactions(address, limit=5)
    explorer_link = bsc_tracker.get_explorer_link(address)
    
    # Форматируем и отправляем
    wallet_info = format_wallet_info(
        address=address,
        blockchain='BNB',
        balance_data=balance_data,
        transactions=transactions,
        explorer_link=explorer_link
    )
    
    await message.answer(wallet_info, parse_mode="HTML", disable_web_page_preview=True)
    await _register_wallet(message, address, "BNB")


async def _register_wallet(message: Message, address: str, blockchain: str) -> None:
    added = await add_tracked_wallet(message.chat.id, address, blockchain)
    if added:
        await message.answer(
            "Кошелек добавлен в отслеживание. Уведомления о новых транзакциях включены.",
            parse_mode="HTML",
        )

# Обработка адресов, отправленных напрямую (без команды /track)
@router.message(F.text)
async def handle_direct_address(message: Message):
    """Обработка адресов, отправленных напрямую"""
    address = message.text.strip()

    if address.startswith("/"):
        return
    
    blockchain = detect_blockchain(address)
    if blockchain == 'UNKNOWN':
        return

    if blockchain == 'TON':
        await process_ton_wallet(message, address)
    elif blockchain == 'ETH':
        # Предлагаем выбрать сеть
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⟠ Ethereum", callback_data=f"track_eth_{address}"),
                InlineKeyboardButton(text="🟡 BSC", callback_data=f"track_bsc_{address}")
            ]
        ])
        await message.answer(
            "🤔 Этот адрес может быть как Ethereum, так и BSC.\n"
            "Выбери сеть:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
