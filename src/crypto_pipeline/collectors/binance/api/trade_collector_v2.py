# binance/api/trade_collector.py -- writing...
import boto3
import requests
import yaml
import time
import logging
import os
import pandas as pd
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TokenConfig:
    symbol: str
    enabled: bool
    limit: int
    collection_frequency: int
    backfill: bool

class BinanceDataCollector:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.tokens = self.parse_token_configs()

        self.session = requests.Session()
        self.api_base_url = 'https://api.binance.us/api/v3'

        self.s3_client = boto3.client('s3')
        self.bucket_name = self.config['s3_settings']['bucket_name']
        self.base_path = self.config['s3_settings']['base_path']

        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
        
    def _parse_token_configs(self) -> List[TokenConfig]:
        default_settings = self.config['default_settings']
        tokens = []

        for token_config in self.config['tokens']:
            backfill = {**default_settings['backfill'],
                        **token_config.get('backfill', {})}
            
            token = TokenConfig(
                symbol=token_config['symbol'],
                enabled=token_config.get(token_config['enabled'], True),
                limit=token_config.get('limit', default_settings['limit']),
                collection_frequency=token_config.get('collection_frequency', default_settings['collection_frequency']),
                backfill=backfill
            )
            tokens.append(token)

        return tokens
    
    def get_trades(self, symbol: str, limit: int, start_time: Optional[int] = None) -> List[Dict]:
        """fetch trades for symbol with optional start time"""

        endpoint = '/trades'

        try:
            params = {
                'symbol': symbol.replace('-', ''),
                'limit': limit
            }
            if start_time:
                params['startTime'] = start_time

            response = self.session.get(
                f'{self.base_api_url}{endpoint}',
                params=params
            )
            response.raise_for_status()

            trades = response.json()
            self._log_trade_summary(trades, symbol)

            return trades
    
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Error fetching trades for {symbol}: {str(e)}')
            return []   
        
    def _log_trade_summary(self, trades: List[Dict], symbol: str):
        if trades:
            first_time = datetime.fromtimestamp(trades[0]['time'] / 1000, UTC)
            last_time = datetime.from_timestamp(trades[-1]['time'] / 1000, UTC)
            self.logger.info(
                f'Fetched {len(trades)} trades for {symbol}\n'
                f'Time range: {first_time} to {last_time}\n'
                f'Span: {last_time - first_time}'
            )
    
    def process_trades(self, trades: List[Dict]) -> pd.DataFrame:
        if not trades:
            return pd.DataFrame()

        df = pd.DataFrame(trades)

        df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)

        return 