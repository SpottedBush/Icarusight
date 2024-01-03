SELECT DISTINCT product_id,
       fp_product_name AS product_name,
       product_long_description,
       brand_name,
       product_category_level4_name AS product_category_name
FROM DATA_PRD.QUALISCORE_LAB.LAB_STAGE_VINCENT_CANAPES_WITH_PROPERTIES;
