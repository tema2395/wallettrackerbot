"""
Модуль для работы с Ethereum blockchain через Etherscan API
"""
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime

class ETHWalletTracker:
    """Класс для отслеживания Ethereum кошельков"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.etherscan.io/v2/api"
        self.api_key = api_key or "YourApiKeyToken"  # Можно работать без ключа с лимитами
        self.chain_id = "1"  # Ethereum mainnet
        self.explorer_url = "https://etherscan.io"
    
    def is_valid_address(self, address: str) -> bool:
        """Проверка валидности Ethereum адреса"""
        return len(address) == 42 and address.startswith('0x')
    
    async def get_balance(self, address: str) -> Optional[Dict]:
        """Получение баланса ETH кошелька"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "chainid": self.chain_id,
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                    "apikey": self.api_key
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"ETH API Response: {data}")  # Debug
                        if data.get('status') == '1':
                            balance_wei = int(data.get('result', 0))
                            balance_eth = balance_wei / 1_000_000_000_000_000_000
                            
                            return {
                                'balance': balance_eth,
                                'currency': 'ETH',
                                'balance_raw': balance_wei
                            }
                        else:
                            print(f"ETH API Error: {data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Ошибка получения баланса ETH: {e}")
        
        return None
    
    async def get_transactions(self, address: str, limit: int = 5) -> List[Dict]:
        """Получение последних транзакций"""
        transactions = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "chainid": self.chain_id,
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": 1,
                    "offset": limit,
                    "sort": "desc",
                    "apikey": self.api_key
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            txs = data.get('result', [])
                            
                            for tx in txs:
                                value = int(tx.get('value', 0)) / 1_000_000_000_000_000_000
                                is_incoming = tx.get('to', '').lower() == address.lower()
                                
                                transactions.append({
                                    'type': 'incoming' if is_incoming else 'outgoing',
                                    'amount': value,
                                    'from': tx.get('from', 'Unknown'),
                                    'to': tx.get('to', 'Unknown'),
                                    'timestamp': int(tx.get('timeStamp', 0)),
                                    'hash': tx.get('hash', 'N/A'),
                                    'status': 'success' if tx.get('txreceipt_status') == '1' else 'failed'
                                })
        
        except Exception as e:
            print(f"Ошибка получения транзакций ETH: {e}")
        
        return transactions[:limit]
    
    def get_explorer_link(self, address: str) -> str:
        """Получение ссылки на explorer"""
        return f"{self.explorer_url}/address/{address}"
