"""
Модуль для работы с TON blockchain через Tonscan API
"""
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime

class TONWalletTracker:
    """Класс для отслеживания TON кошельков"""
    
    def __init__(self):
        self.base_url = "https://toncenter.com/api/v2"
        self.explorer_url = "https://tonscan.org"
    
    def is_valid_address(self, address: str) -> bool:
        """Проверка валидности TON адреса"""
        # TON адреса обычно начинаются с EQ или UQ и имеют определенную длину
        return len(address) == 48 and (address.startswith('EQ') or address.startswith('UQ'))
    
    async def get_balance(self, address: str) -> Optional[Dict]:
        """Получение баланса TON кошелька"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getAddressBalance"
                params = {"address": address}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            balance_nano = int(data.get('result', 0))
                            balance_ton = balance_nano / 1_000_000_000
                            
                            return {
                                'balance': balance_ton,
                                'currency': 'TON',
                                'balance_raw': balance_nano
                            }
        except Exception as e:
            print(f"Ошибка получения баланса TON: {e}")
        
        return None
    
    async def get_transactions(self, address: str, limit: int = 5) -> List[Dict]:
        """Получение последних транзакций"""
        transactions = []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getTransactions"
                params = {
                    "address": address,
                    "limit": limit
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            txs = data.get('result', [])
                            
                            for tx in txs:
                                in_msg = tx.get('in_msg', {})
                                out_msgs = tx.get('out_msgs', [])
                                
                                # Входящая транзакция
                                if in_msg.get('value'):
                                    value = int(in_msg.get('value', 0)) / 1_000_000_000
                                    transactions.append({
                                        'type': 'incoming',
                                        'amount': value,
                                        'from': in_msg.get('source', 'Unknown'),
                                        'timestamp': tx.get('utime', 0),
                                        'hash': tx.get('transaction_id', {}).get('hash', 'N/A')
                                    })
                                
                                # Исходящие транзакции
                                for out_msg in out_msgs:
                                    if out_msg.get('value'):
                                        value = int(out_msg.get('value', 0)) / 1_000_000_000
                                        transactions.append({
                                            'type': 'outgoing',
                                            'amount': value,
                                            'to': out_msg.get('destination', 'Unknown'),
                                            'timestamp': tx.get('utime', 0),
                                            'hash': tx.get('transaction_id', {}).get('hash', 'N/A')
                                        })
        
        except Exception as e:
            print(f"Ошибка получения транзакций TON: {e}")
        
        return transactions[:limit]
    
    def get_explorer_link(self, address: str) -> str:
        """Получение ссылки на explorer"""
        return f"{self.explorer_url}/address/{address}"
