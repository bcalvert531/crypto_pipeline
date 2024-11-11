
  
    
    

    create  table
      "crypto_trading"."main"."minute_ohlcv__dbt_tmp"
  
    as (
      -- mart/minute_ohlcv.sql
WITH minute_trades AS (
    SELECT
        DATE_TRUNC('minute', traded_at) AS trading_minute,
        price,
        qty,
        tick_volume,
        traded_at  
    FROM "crypto_trading"."main"."stg_trades"
)

SELECT 
    trading_minute,
    FIRST_VALUE(price) OVER (
        PARTITION BY trading_minute
        ORDER BY traded_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    LAST_VALUE(price) OVER (
        PARTITION BY trading_minute
        ORDER BY traded_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS close,
    SUM(tick_volume) AS volume,
    COUNT(*) AS trade_count
FROM minute_trades
GROUP BY trading_minute
ORDER BY trading_minute
    );
  
  