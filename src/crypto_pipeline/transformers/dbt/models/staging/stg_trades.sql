-- staging/stg_trades.sql
SELECT
    id,
    price,
    qty,
    quoteQty,
    time AS traded_at,
    isBuyerMaker,
    isBestMatch,
    tick_volume,
    tick_direction,
    MAKE_DATE(year, month, day) AS partition_date
FROM {{ source('raw', 'trades') }}
WHERE price > 0
