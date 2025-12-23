"""
Уведомления о новых транзакциях
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from aiogram import Bot

from services.trackers import ton_tracker, eth_tracker, bsc_tracker
from utils import format_transaction

logger = logging.getLogger(__name__)


@dataclass
class TrackedWallet:
    address: str
    blockchain: str
    last_seen_hash: Optional[str] = None


_tracked_wallets: Dict[int, List[TrackedWallet]] = {}
_lock = asyncio.Lock()


def _get_tracker(blockchain: str):
    if blockchain == "TON":
        return ton_tracker
    if blockchain == "ETH":
        return eth_tracker
    if blockchain == "BNB":
        return bsc_tracker
    raise ValueError(f"Unknown blockchain: {blockchain}")


def list_tracked_wallets(chat_id: int) -> List[TrackedWallet]:
    return list(_tracked_wallets.get(chat_id, []))


async def add_tracked_wallet(chat_id: int, address: str, blockchain: str) -> bool:
    async with _lock:
        wallets = _tracked_wallets.setdefault(chat_id, [])
        for wallet in wallets:
            if wallet.address == address and wallet.blockchain == blockchain:
                return False

        wallet = TrackedWallet(address=address, blockchain=blockchain)
        wallets.append(wallet)

    tracker = _get_tracker(blockchain)
    try:
        txs = await tracker.get_transactions(address, limit=1, use_cache=False)
        if txs:
            wallet.last_seen_hash = txs[0].get("hash")
    except Exception:
        logger.exception("Failed to initialize last seen tx for %s", address)

    return True


async def remove_tracked_wallet(chat_id: int, address: str) -> bool:
    async with _lock:
        wallets = _tracked_wallets.get(chat_id, [])
        removed = False
        for wallet in list(wallets):
            if wallet.address == address:
                wallets.remove(wallet)
                removed = True
        return removed
    return False


def _build_notification_message(
    wallet: TrackedWallet, transactions: List[dict], explorer_link: str
) -> str:
    short_address = f"{wallet.address[:8]}...{wallet.address[-6:]}"
    message = (
        f"Новые транзакции для <b>{wallet.blockchain}</b> "
        f"<code>{short_address}</code>\n\n"
    )

    for tx in transactions:
        message += f"{format_transaction(tx, wallet.blockchain)}\n\n"

    message += f'<a href="{explorer_link}">Открыть в Explorer</a>'
    return message


async def _check_wallets(bot: Bot) -> None:
    items: List[tuple[int, TrackedWallet]] = []
    async with _lock:
        for chat_id, wallets in _tracked_wallets.items():
            for wallet in wallets:
                items.append((chat_id, wallet))

    for chat_id, wallet in items:
        tracker = _get_tracker(wallet.blockchain)
        try:
            txs = await tracker.get_transactions(wallet.address, limit=5, use_cache=False)
        except Exception:
            logger.exception("Failed to fetch transactions for %s", wallet.address)
            continue

        if not txs:
            continue

        new_txs: List[dict] = []
        for tx in txs:
            tx_hash = tx.get("hash")
            if wallet.last_seen_hash and tx_hash == wallet.last_seen_hash:
                break
            new_txs.append(tx)

        if not new_txs:
            continue

        wallet.last_seen_hash = new_txs[0].get("hash")
        explorer_link = tracker.get_explorer_link(wallet.address)
        message = _build_notification_message(wallet, new_txs, explorer_link)

        try:
            await bot.send_message(
                chat_id,
                message,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception:
            logger.exception("Failed to send notification to chat %s", chat_id)


async def monitor_wallets(bot: Bot, interval_seconds: int) -> None:
    logger.info("Notification loop started with interval=%s seconds", interval_seconds)
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            await _check_wallets(bot)
        except asyncio.CancelledError:
            logger.info("Notification loop stopped")
            raise
        except Exception:
            logger.exception("Notification loop error")
