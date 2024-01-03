SELECT DISTINCT ARRAY_AGG(product_id) AS product_ids,
                product_property_id, 
                product_property_name, 
                product_property_value
FROM DATA_PRD.QUALISCORE_LAB.LAB_STAGE_VINCENT_CANAPES_WITH_PROPERTIES 
GROUP BY (product_property_id, product_property_value, product_property_name);
