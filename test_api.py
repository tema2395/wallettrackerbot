"""
Тестовый скрипт для проверки работы API блокчейнов
"""
import asyncio
import sys
from blockchain import TONWalletTracker, ETHWalletTracker, BSCWalletTracker

# Тестовые адреса (публичные, известные кошельки)
TEST_ADDRESSES = {
    'TON': 'EQD1Lp1KcmGHFpE8eIvL1mnHT83b4HdB8HJxuSfq6Rq4zGyN',  # Пример TON адреса
    'ETH': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',  # Пример ETH адреса
    'BSC': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',  # Пример BSC адреса
}

async def test_ton():
    """Тест TON API"""
    print("\n" + "="*50)
    print("🧪 Тестирование TON API")
    print("="*50)
    
    tracker = TONWalletTracker()
    address = TEST_ADDRESSES['TON']
    
    print(f"📍 Адрес: {address}")
    print(f"✅ Валидность: {tracker.is_valid_address(address)}")
    
    # Тест баланса
    print("\n💰 Получение баланса...")
    balance = await tracker.get_balance(address)
    if balance:
        print(f"   Баланс: {balance['balance']} {balance['currency']}")
    else:
        print("   ❌ Ошибка получения баланса")
    
    # Тест транзакций
    print("\n📊 Получение транзакций...")
    transactions = await tracker.get_transactions(address, limit=3)
    if transactions:
        print(f"   Найдено транзакций: {len(transactions)}")
        for i, tx in enumerate(transactions[:3], 1):
            print(f"   {i}. {tx['type']}: {tx['amount']} TON")
    else:
        print("   ❌ Транзакции не найдены")
    
    print(f"\n🔗 Explorer: {tracker.get_explorer_link(address)}")

async def test_eth():
    """Тест Ethereum API"""
    print("\n" + "="*50)
    print("🧪 Тестирование Ethereum API")
    print("="*50)
    
    tracker = ETHWalletTracker()
    address = TEST_ADDRESSES['ETH']
    
    print(f"📍 Адрес: {address}")
    print(f"✅ Валидность: {tracker.is_valid_address(address)}")
    
    # Тест баланса
    print("\n💰 Получение баланса...")
    balance = await tracker.get_balance(address)
    if balance:
        print(f"   Баланс: {balance['balance']} {balance['currency']}")
    else:
        print("   ❌ Ошибка получения баланса")
    
    # Тест транзакций
    print("\n📊 Получение транзакций...")
    transactions = await tracker.get_transactions(address, limit=3)
    if transactions:
        print(f"   Найдено транзакций: {len(transactions)}")
        for i, tx in enumerate(transactions[:3], 1):
            print(f"   {i}. {tx['type']}: {tx['amount']} ETH")
    else:
        print("   ❌ Транзакции не найдены")
    
    print(f"\n🔗 Explorer: {tracker.get_explorer_link(address)}")

async def test_bsc():
    """Тест BSC API"""
    print("\n" + "="*50)
    print("🧪 Тестирование BSC API")
    print("="*50)
    
    tracker = BSCWalletTracker()
    address = TEST_ADDRESSES['BSC']
    
    print(f"📍 Адрес: {address}")
    print(f"✅ Валидность: {tracker.is_valid_address(address)}")
    
    # Тест баланса
    print("\n💰 Получение баланса...")
    balance = await tracker.get_balance(address)
    if balance:
        print(f"   Баланс: {balance['balance']} {balance['currency']}")
    else:
        print("   ❌ Ошибка получения баланса")
    
    # Тест транзакций
    print("\n📊 Получение транзакций...")
    transactions = await tracker.get_transactions(address, limit=3)
    if transactions:
        print(f"   Найдено транзакций: {len(transactions)}")
        for i, tx in enumerate(transactions[:3], 1):
            print(f"   {i}. {tx['type']}: {tx['amount']} BNB")
    else:
        print("   ❌ Транзакции не найдены")
    
    print(f"\n🔗 Explorer: {tracker.get_explorer_link(address)}")

async def main():
    """Главная функция"""
    print("\n" + "="*50)
    print("🧪 ТЕСТИРОВАНИЕ WALLET TRACKER BOT")
    print("="*50)
    print("\nЭтот скрипт проверит работу всех API блокчейнов")
    print("Используются тестовые публичные адреса\n")
    
    # Запуск всех тестов
    await test_ton()
    await test_eth()
    await test_bsc()
    
    print("\n" + "="*50)
    print("✅ Тестирование завершено!")
    print("="*50)
    print("\nЕсли все API работают корректно, можете запускать бота:")
    print("  python bot.py")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Тестирование прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
