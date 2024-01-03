SELECT
    product_property_id,
    product_property_value,
    ARRAY_DISTINCT(ARRAY_AGG(product_id)) AS product_ids,
    ARRAY_DISTINCT(ARRAY_AGG(product_property_name)) AS product_property_names
FROM DATA_PRD.QUALISCORE_LAB.LAB_STAGE_VINCENT_CANAPES_WITH_PROPERTIES 
GROUP BY (product_property_id, product_property_value);
