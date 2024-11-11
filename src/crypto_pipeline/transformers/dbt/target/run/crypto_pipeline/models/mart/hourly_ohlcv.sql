
  
    
    

    create  table
      "crypto_trading"."main"."hourly_ohlcv__dbt_tmp"
  
    as (
      -- mart/hourly_ohlcv.sql
WITH hourly_trades AS (
    SELECT
        DATE_TRUNC('hour', traded_at) AS trading_hour,
        price,
        qty,
        tick_volume
    FROM "crypto_trading"."main"."stg_trades"
)

SELECT 
    trading_hour,
    FIRST_VALUE(price) OVER (
        PARTITION BY trading_hour
        ORDER BY trading_hour
    ) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST_VALUE(price) OVER (
        PARTITION BY trading_hour
        ORDER BY trading_hour
    ) AS close,
    SUM(tick_volume) AS volume,
    COUNT(*) AS trade_count
FROM hourly_trades
GROUP BY trading_hour
    );
  
  