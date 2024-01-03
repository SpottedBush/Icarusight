WITH RankedProducts AS (
SELECT *, ROW_NUMBER() OVER (PARTITION BY product_category_name ORDER BY product_name) AS rn FROM(
  SELECT *
  FROM (
  SELECT product_id,
         product_name,
         product_category_name,
         seller_name,
         brand_name,
         product_long_description,
         ROW_NUMBER() OVER(PARTITION BY product_id ORDER BY seller_name DESC) rn2
         FROM QUALISCORE_LAB.LAB_CATEGORIES_DATAPOOL
         ) a
WHERE rn2 = 1)
)
SELECT * FROM RankedProducts WHERE rn <= 10;