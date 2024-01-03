SELECT
    pilot.product_id AS ref_id,
    pilot.product_name AS ref_name,
    pilot.product_category_name AS ref_category_name,
    pilot2.product_id AS related_id,
    pilot2.product_name AS related_name,
    co.couple_view_count,
    pilot2.product_category_name AS related_category_name,
    pilot2.brand_name AS related_brand_name,
    pilot2.product_long_description AS related_long_description
FROM DATA_PRD.QUALISCORE_LAB.PILOT_BASED_DATAPOOL AS pilot
INNER JOIN DATA_PRD.SEARCH_SMT.SMT_SCH_AGG_PRODUCT_COUPLE_VIEW AS co ON pilot.product_id = UPPER(co.first_product_id) AND co.couple_view_count > 1
INNER JOIN DATA_PRD.QUALISCORE_LAB.PILOT_BASED_DATAPOOL AS pilot2 ON UPPER(co.second_product_id)=pilot2.product_id;