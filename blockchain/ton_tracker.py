"""
Модуль для работы с TON blockchain через Tonscan API
"""
import aiohttp
import logging
from typing import Dict, List, Optional

from utils.network import AsyncRateLimiter, TTLCache
from utils.validators import is_valid_ton_address

logger = logging.getLogger(__name__)

class TONWalletTracker:
    """Класс для отслеживания TON кошельков"""
    
    def __init__(self, cache_ttl_seconds: int = 30, rate_limit_min_interval: float = 0.25):
        self.base_url = "https://toncenter.com/api/v2"
        self.explorer_url = "https://tonscan.org"
        self._timeout = aiohttp.ClientTimeout(total=10)
        self._balance_cache = TTLCache(cache_ttl_seconds)
        self._tx_cache = TTLCache(cache_ttl_seconds)
        self._rate_limiter = AsyncRateLimiter(rate_limit_min_interval)
    
    def is_valid_address(self, address: str) -> bool:
        """Проверка валидности TON адреса"""
        # TON адреса обычно начинаются с EQ или UQ и имеют определенную длину
        return is_valid_ton_address(address)

    async def _request_json(self, endpoint: str, params: Dict) -> Optional[Dict]:
        await self._rate_limiter.wait()
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning("TON API status=%s for %s", response.status, endpoint)
                    return None
                return await response.json()
    
    async def get_balance(self, address: str, use_cache: bool = True) -> Optional[Dict]:
        """Получение баланса TON кошелька"""
        cache_key = f"balance:{address}"
        if use_cache:
            cached = self._balance_cache.get(cache_key)
            if cached is not None:
                return cached
        try:
            params = {"address": address}
            data = await self._request_json("getAddressBalance", params)
            if data and data.get("ok"):
                balance_nano = int(data.get("result", 0))
                balance_ton = balance_nano / 1_000_000_000

                result = {
                    "balance": balance_ton,
                    "currency": "TON",
                    "balance_raw": balance_nano,
                }
                self._balance_cache.set(cache_key, result)
                return result
        except Exception as e:
            logger.exception("Ошибка получения баланса TON")
        
        return None
    
    async def get_transactions(
        self, address: str, limit: int = 5, use_cache: bool = True
    ) -> List[Dict]:
        """Получение последних транзакций"""
        transactions = []
        cache_key = f"tx:{address}:{limit}"
        if use_cache:
            cached = self._tx_cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            params = {"address": address, "limit": limit}
            data = await self._request_json("getTransactions", params)
            if data and data.get("ok"):
                txs = data.get("result", [])

                for tx in txs:
                    in_msg = tx.get("in_msg", {})
                    out_msgs = tx.get("out_msgs", [])

                    # Входящая транзакция
                    if in_msg.get("value"):
                        value = int(in_msg.get("value", 0)) / 1_000_000_000
                        transactions.append(
                            {
                                "type": "incoming",
                                "amount": value,
                                "from": in_msg.get("source", "Unknown"),
                                "timestamp": tx.get("utime", 0),
                                "hash": tx.get("transaction_id", {}).get("hash", "N/A"),
                            }
                        )

                    # Исходящие транзакции
                    for out_msg in out_msgs:
                        if out_msg.get("value"):
                            value = int(out_msg.get("value", 0)) / 1_000_000_000
                            transactions.append(
                                {
                                    "type": "outgoing",
                                    "amount": value,
                                    "to": out_msg.get("destination", "Unknown"),
                                    "timestamp": tx.get("utime", 0),
                                    "hash": tx.get("transaction_id", {}).get("hash", "N/A"),
                                }
                            )
        
        except Exception:
            logger.exception("Ошибка получения транзакций TON")
        
        result = transactions[:limit]
        self._tx_cache.set(cache_key, result)
        return result
    
    def get_explorer_link(self, address: str) -> str:
        """Получение ссылки на explorer"""
        return f"{self.explorer_url}/address/{address}"
