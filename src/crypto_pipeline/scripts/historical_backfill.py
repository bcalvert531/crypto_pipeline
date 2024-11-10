from crypto_pipeline.collectors.binance_collector import BinanceDataCollector

if __name__ == "__main__":
    collector = BinanceDataCollector(
        bucket_name='crypto-pipeline-dev-data'
    )

    symbol = 'BTC-USDT'

    num_trades = collector.collect_and_store(symbol)
    print(f'Collected {num_trades} trades for {symbol}')