-- mart/minute_ohlcv.sql
WITH minute_trades AS (
    SELECT
        DATE_TRUNC('minute', traded_at) AS trading_minute,
        traded_at,
        price,
        qty,
        tick_volume,
        FIRST_VALUE(price) OVER (
            PARTITION BY trading_minute
            ORDER BY traded_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS open_price,
    LAST_VALUE(price) OVER (
            PARTITION BY trading_minute
            ORDER BY traded_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS close_price
    FROM {{ ref('stg_trades') }}
)

SELECT 
    trading_minute,
    MAX(open_price) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    MAX(close_price) AS close,
    SUM(tick_volume) AS volume,
    COUNT(*) AS trade_count
FROM minute_trades
GROUP BY trading_minute
ORDER BY trading_minute