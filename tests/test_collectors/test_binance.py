from crypto_pipeline.collectors.binance_collector import BinanceDataCollector

def test_fetch_trades():
    # tests fetching binance trades without s3 upload
    collector = BinanceDataCollector(bucket_name='dummy-bucket')

    symbol = 'BTC-USD'
    trades = collector.get_trades(symbol)
    
    if trades:
        df = collector.process_trades(trades)
        print(f"\nDataset Shape: {df.shape}")
        print("\nTime Range Info:")
        print(f"Start: {df['time'].min()}")
        print(f"End: {df['time'].max()}")
        print(f"Duration: {df['time'].max() - df['time'].min()}")
        print("\nFirst few trades:")
        print(df.head().to_string())
    else:
        print("No trades fetched")

if __name__ == "__main__":
    test_fetch_trades() 