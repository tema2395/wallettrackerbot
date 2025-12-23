"""
Валидация адресов кошельков и определение блокчейна
"""
from __future__ import annotations

import re

_ETH_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_TON_ADDRESS_RE = re.compile(r"^(EQ|UQ)[A-Za-z0-9_-]{46}$")


def is_valid_eth_address(address: str) -> bool:
    """Проверка валидности адреса Ethereum/BSC"""
    return bool(_ETH_ADDRESS_RE.match(address))


def is_valid_ton_address(address: str) -> bool:
    """Проверка валидности адреса TON"""
    return bool(_TON_ADDRESS_RE.match(address))


def detect_blockchain(address: str) -> str:
    """Автоматическое определение типа блокчейна по адресу"""
    if is_valid_ton_address(address):
        return "TON"
    if is_valid_eth_address(address):
        return "ETH"
    return "UNKNOWN"
