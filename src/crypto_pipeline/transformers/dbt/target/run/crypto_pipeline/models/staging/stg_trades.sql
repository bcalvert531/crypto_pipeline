
  
  create view "crypto_trading"."main"."stg_trades__dbt_tmp" as (
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
FROM "crypto_trading"."raw"."trades"
WHERE price > 0
  );
