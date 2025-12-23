"""
Утилиты для форматирования данных
"""
from datetime import datetime
from typing import Dict, List

def format_balance(balance_data: Dict) -> str:
    """Форматирование баланса для отображения"""
    if not balance_data:
        return "❌ Не удалось получить баланс"
    
    balance = balance_data['balance']
    currency = balance_data['currency']
    
    return f"💰 Баланс: {balance:.6f} {currency}"

def format_transaction(tx: Dict, blockchain: str) -> str:
    """Форматирование транзакции для отображения"""
    tx_type = tx['type']
    amount = tx['amount']
    timestamp = tx['timestamp']
    
    # Форматирование даты
    try:
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        date = "Unknown"
    
    # Иконка в зависимости от типа транзакции
    icon = "📥" if tx_type == "incoming" else "📤"
    
    # Форматирование адресов
    if tx_type == "incoming":
        address = tx.get('from', 'Unknown')
        address_label = "От"
    else:
        address = tx.get('to', 'Unknown')
        address_label = "Кому"
    
    # Сокращение адреса
    if len(address) > 10:
        short_address = f"{address[:6]}...{address[-4:]}"
    else:
        short_address = address
    
    # Статус (если есть)
    status = ""
    if 'status' in tx:
        status = "✅" if tx['status'] == 'success' else "❌"
    
    # Хеш транзакции
    tx_hash = tx.get('hash', 'N/A')
    if len(tx_hash) > 10:
        short_hash = f"{tx_hash[:6]}...{tx_hash[-4:]}"
    else:
        short_hash = tx_hash
    
    return (
        f"{icon} {tx_type.capitalize()}: {amount:.6f}\n"
        f"   {address_label}: {short_address}\n"
        f"   Дата: {date}\n"
        f"   Hash: {short_hash} {status}"
    )

def format_wallet_info(address: str, blockchain: str, balance_data: Dict, transactions: List[Dict], explorer_link: str) -> str:
    """Форматирование полной информации о кошельке"""
    
    # Заголовок
    blockchain_emoji = {
        'TON': '💎',
        'ETH': '⟠',
        'BNB': '🟡'
    }
    emoji = blockchain_emoji.get(blockchain, '💼')
    
    message = f"{emoji} <b>{blockchain} Кошелек</b>\n\n"
    
    # Адрес
    short_address = f"{address[:8]}...{address[-6:]}"
    message += f"📍 Адрес: <code>{short_address}</code>\n\n"
    
    # Баланс
    message += format_balance(balance_data) + "\n\n"
    
    # Транзакции
    if transactions:
        message += "📊 <b>Последние транзакции:</b>\n\n"
        for i, tx in enumerate(transactions[:5], 1):
            message += f"{i}. {format_transaction(tx, blockchain)}\n\n"
    else:
        message += "📊 Транзакции не найдены\n\n"
    
    # Ссылка на explorer
    message += f'🔗 <a href="{explorer_link}">Смотреть в Explorer</a>'
    
    return message

def detect_blockchain(address: str) -> str:
    """Автоматическое определение типа блокчейна по адресу"""
    if len(address) == 48 and (address.startswith('EQ') or address.startswith('UQ')):
        return 'TON'
    elif len(address) == 42 and address.startswith('0x'):
        # По умолчанию считаем ETH, но может быть и BSC
        return 'ETH'
    else:
        return 'UNKNOWN'
