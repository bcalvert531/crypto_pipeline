# binance/api/trade_collector.py
import pandas as pd 
import boto3
import requests
from datetime import datetime, timedelta, UTC
import time
import logging
import os
from dotenv import load_dotenv
load_dotenv()

class BinanceDataCollector:
    def __init__(self, bucket_name, base_path='raw/trades'):
        self.session = requests.Session()
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.base_path = base_path
        self.api_base_url = 'https://api.binance.us/api/v3'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s -%(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_trades(self, symbol, limit=1000):
        """
        Fetch most recent trades for symbol.

        Args:
            symbol (str): trading pair, e.g. 'BTC-USD'
            limit (int): number of trades per request, max=1000
        """
        endpoint = '/trades'
        
        try:
            params = {
                'symbol': symbol.replace('-', ''),  # Convert BTC-USD to BTCUSD
                'limit': limit
            }

            response = self.session.get(
                f"{self.api_base_url}{endpoint}",
                params=params
            )
            response.raise_for_status()

            trades = response.json()
            
            if trades:
                first_time = datetime.fromtimestamp(trades[0]['time'] / 1000, UTC)
                last_time = datetime.fromtimestamp(trades[-1]['time'] / 1000, UTC)
                time_span = last_time - first_time
                
                self.logger.info(
                    f"Fetched {len(trades)} trades for {symbol}\n"
                    f"Time range: {first_time} to {last_time}\n"
                    f"Span: {time_span}"
                )
                
            return trades

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching trades: {str(e)}")
            return []

    
    def process_trades(self, trades):
        df = pd.DataFrame(trades)

        df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)

        df['price'] = df['price'].astype(float)
        df['qty'] = df['qty'].astype(float)

        df['tick_volume'] = df['price'] * df['qty']

        if 'isBuyerMaker' in df.columns:
            df['tick_direction'] = df['isBuyerMaker'].map({True: -1, False: 1})

        df = df.sort_values('time')

        return df


    def save_to_s3(self, df, symbol):
        for date, group in df.groupby(df['time'].dt.date):
            year = date.year
            month = str(date.month).zfill(2)
            day = str(date.day).zfill(2)

            s3_path = f"{self.base_path}/{year}/{month}/{day}/{symbol.lower()}_trades.csv"

            csv_buffer = group.to_csv(index=False)

            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_path,
                    Body=csv_buffer,
                    ServerSideEncryption='AES256'
                )
                self.logger.info(f"Successfully uploaded {symbol} trades to {s3_path}")

            except Exception as e:
                self.logger.error(f"Error uploading to S3: {str(e)}")


    def collect_and_store(self, symbol='BTC-USDT'):
        self.logger.info(f"Starting data collection for {symbol}")

        trades = self.get_trades(symbol)

        if not trades:
            self.logger.warning(f'No trades found for {symbol}')
            return

        df = self.process_trades(trades)

        self.save_to_s3(df, symbol)

        self.logger.info(f'Completed data collection for {symbol}')

        return len(df)



