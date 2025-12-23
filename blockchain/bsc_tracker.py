"""
Модуль для работы с Binance Smart Chain через BscScan API
"""
import aiohttp
import logging
from typing import Dict, List, Optional

from utils.network import AsyncRateLimiter, TTLCache
from utils.validators import is_valid_eth_address

logger = logging.getLogger(__name__)

class BSCWalletTracker:
    """Класс для отслеживания BSC кошельков"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl_seconds: int = 30,
        rate_limit_min_interval: float = 0.25,
    ):
        self.base_url = "https://api.etherscan.io/v2/api"
        self.api_key = api_key or "YourApiKeyToken"
        self.chain_id = "56"  # BSC mainnet
        self.explorer_url = "https://bscscan.com"
        self._timeout = aiohttp.ClientTimeout(total=10)
        self._balance_cache = TTLCache(cache_ttl_seconds)
        self._tx_cache = TTLCache(cache_ttl_seconds)
        self._rate_limiter = AsyncRateLimiter(rate_limit_min_interval)
    
    def is_valid_address(self, address: str) -> bool:
        """Проверка валидности BSC адреса (такой же формат как у ETH)"""
        return is_valid_eth_address(address)

    async def _request_json(self, params: Dict) -> Optional[Dict]:
        await self._rate_limiter.wait()
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.warning("BSC API status=%s for %s", response.status, params.get("action"))
                    return None
                return await response.json()
    
    async def get_balance(self, address: str, use_cache: bool = True) -> Optional[Dict]:
        """Получение баланса BNB кошелька"""
        cache_key = f"balance:{address}"
        if use_cache:
            cached = self._balance_cache.get(cache_key)
            if cached is not None:
                return cached
        try:
            params = {
                "chainid": self.chain_id,
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": self.api_key,
            }

            data = await self._request_json(params)
            if data and data.get("status") == "1":
                balance_wei = int(data.get("result", 0))
                balance_bnb = balance_wei / 1_000_000_000_000_000_000

                result = {
                    "balance": balance_bnb,
                    "currency": "BNB",
                    "balance_raw": balance_wei,
                }
                self._balance_cache.set(cache_key, result)
                return result
            if data and data.get("status") == "0":
                logger.warning("BSC API error: %s", data.get("message", "Unknown error"))
        except Exception:
            logger.exception("Ошибка получения баланса BNB")
        
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
                "apikey": self.api_key,
            }

            data = await self._request_json(params)
            if data and data.get("status") == "1":
                txs = data.get("result", [])

                for tx in txs:
                    value = int(tx.get("value", 0)) / 1_000_000_000_000_000_000
                    is_incoming = tx.get("to", "").lower() == address.lower()

                    tx_status = tx.get("txreceipt_status")
                    status = "unknown" if tx_status is None else "success" if tx_status == "1" else "failed"

                    transactions.append(
                        {
                            "type": "incoming" if is_incoming else "outgoing",
                            "amount": value,
                            "from": tx.get("from", "Unknown"),
                            "to": tx.get("to", "Unknown"),
                            "timestamp": int(tx.get("timeStamp", 0)),
                            "hash": tx.get("hash", "N/A"),
                            "status": status,
                        }
                    )
            if data and data.get("status") == "0":
                logger.warning("BSC API error: %s", data.get("message", "Unknown error"))
        
        except Exception:
            logger.exception("Ошибка получения транзакций BNB")
        
        result = transactions[:limit]
        self._tx_cache.set(cache_key, result)
        return result
    
    def get_explorer_link(self, address: str) -> str:
        """Получение ссылки на explorer"""
        return f"{self.explorer_url}/address/{address}"
