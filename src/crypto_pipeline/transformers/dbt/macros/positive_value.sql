# macros/positive_value.sql
{% macro positive_value(model, column_name) %}
SELECT 
    *
FROM {{ model }}
WHERE {{ column_name }} <= 0 
{% endmacro %}