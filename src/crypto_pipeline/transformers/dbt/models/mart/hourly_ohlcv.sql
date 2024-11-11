-- mart/hourly_ohlcv.sql
WITH hourly_trades AS (
    SELECT
        DATE_TRUNC('hour', traded_at) AS trading_hour,
        traded_at,
        price,
        qty,
        tick_volume,
        FIRST_VALUE(price) OVER (
            PARTITION BY traded_at
            ORDER BY traded_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS open_price,
        LAST_VALUE(price) OVER (
            PARTITION BY traded_at
            ORDER BY traded_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS close_price,
    FROM {{ ref('stg_trades') }}
)

SELECT 
    trading_hour,
    MAX(open_price) AS open,
    MAX(price) AS high,
    MIN(price) AS low,
    MAX(close_price) AS close,
    SUM(tick_volume) AS volume,
    COUNT(*) AS trade_count
FROM hourly_trades
GROUP BY trading_hour
ORDER BY trading_hour
