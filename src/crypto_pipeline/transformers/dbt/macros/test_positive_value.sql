# macros/test_positive_value.sql
{% macro test_positive_value(model, column_name) %}
SELECT 
    *
FROM {{ model }}
WHERE {{ column_name }} <= 0 
{% endmacro %}