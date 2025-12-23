"""
Единая инициализация трекеров блокчейнов
"""
from blockchain import TONWalletTracker, ETHWalletTracker, BSCWalletTracker
from config import config

ton_tracker = TONWalletTracker(
    cache_ttl_seconds=config.cache_ttl_seconds,
    rate_limit_min_interval=config.rate_limit_min_interval,
)
eth_tracker = ETHWalletTracker(
    api_key=config.etherscan_api_key,
    cache_ttl_seconds=config.cache_ttl_seconds,
    rate_limit_min_interval=config.rate_limit_min_interval,
)
bsc_tracker = BSCWalletTracker(
    api_key=config.bscscan_api_key,
    cache_ttl_seconds=config.cache_ttl_seconds,
    rate_limit_min_interval=config.rate_limit_min_interval,
)

__all__ = ["ton_tracker", "eth_tracker", "bsc_tracker"]
