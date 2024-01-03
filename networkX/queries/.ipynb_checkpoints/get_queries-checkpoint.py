from Icarusight.Icarusight.utils import cleaning_strings
from cdiscount import config
from cdiscount import snowflake
#import os

#os.chdir("Icarusight")
#secrets = config.load_secrets('queries/mes-secrets.yml', key='snowflake')
small_database_query_path = 'queries/GetSmolDatapool.sql'
pilot_database_query_path = 'queries/GetPilotBasedDataPool_WHOLE.sql'
property_model_reference_path = 'queries/GetPropertyModelReference.sql'
co_viewed_query_path = 'queries/GetCoViewedProducts.sql'
product_properties_query_path = 'queries/GetProductProperties.sql'
product_canape_query_path = 'queries/GetProductCanape_WHOLE.sql'
#con = snowflake.get_snowflake_connection(**secrets)


def query_pilot_product_df(con):
    product_df = snowflake.query_snowflake_to_df(pilot_database_query_path, con=con)
    product_df['product_long_description'] = product_df['product_long_description'].apply(cleaning_strings)
    product_df['product_name'] = product_df['product_name'].apply(cleaning_strings)
    return product_df


def query_canape_product_df(con):
    return snowflake.query_snowflake_to_df(product_canape_query_path, con=con)


def query_product_properties_df(con):
    return snowflake.query_snowflake_to_df(product_properties_query_path, con=con)


def query_co_viewed_df(con):
    co_viewed_df = snowflake.query_snowflake_to_df(co_viewed_query_path, con=con)
    co_viewed_df['ref_name'] = co_viewed_df['ref_name'].apply(cleaning_strings)
    co_viewed_df['related_name'] = co_viewed_df['related_name'].apply(cleaning_strings)
    return co_viewed_df
