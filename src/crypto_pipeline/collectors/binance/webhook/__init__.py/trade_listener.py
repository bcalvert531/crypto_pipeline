# binance/webhook/trade_listener.py
from dataclasses import dataclass
import websockets
import asyncio
import json
import duckdb
import redis
from typing import Dict, List
from datetime import datetime, timezone

@dataclass
class TradeConfig:
    symbols: List[str]
    candlestick_interval: str = '1m'
    max_lookback: int = 1000

class MarketDataService:
    def __init__(self):
        self.redis = redis.Redis(decode_response=True)
