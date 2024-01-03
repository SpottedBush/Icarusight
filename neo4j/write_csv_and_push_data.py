from cdiscount import config
from cdiscount import snowflake
import re
from neo4j import GraphDatabase, basic_auth
import pandas as pd
from unidecode import unidecode


def cleaning_strings(strings: pd.Series):
    return (
        strings.str.lower()
        .str.replace(
            r'(\d+)[\.,\s]0', r'\1', regex=True
        )  # Remove ".0" ",0" and " 0" at the end of float numbers. Ex: 2.0 => 2
        .str.replace(r'(\d+)[,.](\d+)', r'\1\2', regex=True)
        .str.replace(
            r'(^|\s)(\d+)(\s)([A-Za-z0-9À-ÿ])', r'\1\2\4', regex=True
        )  # Remove white space between digits and following string. Ex: 5 ah => 5ah. Bad ex: ps 5 noir => ps 5noir
        .str.replace(
            '[^A-Za-z0-9À-ÿ.,]', ' ', regex=True
        )  # Remove special characters and keep accents. Accents are usefull for BERT embeddings but cause bad string normalization. Ex canapé and canape will be different strings
        .str.replace('\s+', ' ', regex=True)  # Remove consecutive whitespaces
        .str.replace(r'(\d+)\sx\s(\d+)', r'\1x\2', regex=True)
        # Remove white space after words "avec", "sans" and "pour". Ex: avec batterie => avec_batterie
        .str.replace('avec ', 'avec_', regex=False)
        .str.replace('sans ', 'sans_', regex=False)
        .str.replace('pour ', 'pour_', regex=False)
        .apply(unidecode)  # Remove accents
        .str.strip()
    )


def write_csv_from_snowflake():
    """
    proceed to write csv from the data queried from snowflake. Write the products_sellers.csv and the product_property.csv which contains all the relationships.
    @return: None
    @rtype: None
    """
    secrets = config.load_secrets('secrets.yml', key='snowflake')
    products_properties_query = "queries/get_products_properties.sql"
    products_sellers_query = "queries/get_products_sellers.sql"
    with snowflake.get_snowflake_connection(**secrets) as con:
        products_properties_df = snowflake.query_snowflake_to_df(products_properties_query, con=con)
        products_sellers_df = snowflake.query_snowflake_to_df(products_sellers_query, con=con)
        cleaning_strings(products_sellers_df["product_long_description"])
        products_properties_df.to_csv("csv_files/products_properties.csv", index=False, sep='\u0001')
        products_sellers_df.to_csv("csv_files/products_sellers.csv", index=False, sep='\u0001')


def push_data_to_neo4j(cleaning_before_pushing=True, index=True, nodes=True, relationship=True, weighted_relationship=False):
    """
    Proceeds to push all the data contained in the csv to the neo4j docker image. It creates indexes, nodes and relationships
    This model contains : nodes class product and property and nodes relationships "has" (product->property) and "Neighbor" (product->product)
    @param index: Whether to push the index to Neo4j docker image
    @type index: Boolean
    @param nodes: Whether to push the nodes to Neo4j docker image
    @type nodes: Boolean
    @param relationship: Whether to push the relationships to Neo4j docker image
    @type relationship: Boolean
    @param weighted_relationship: Whether to add weights to the relationships
    @type weighted_relationship: Boolean
    @return: None
    @rtype: None
    """
    username = "neo4j"
    password = "zDje683kEKpo23"
    driver = GraphDatabase.driver(uri="bolt://a08datasc002.cdbdx.biz:7687", auth=(username, password))

    
    cleaning_all = '''
    MATCH (n)
    DETACH DELETE n
    '''
    
    products_idx = '''
    CREATE INDEX products_constraint IF NOT EXISTS FOR (n:Product) ON n.product_id;
    '''
    property_idx = '''
    CREATE INDEX property_constraint IF NOT EXISTS FOR (n:Property) ON n.product_property_value;
    '''
    # product_property_value,product_id,product_category_level4_id,product_category_level4_name,product_long_description
    create_products_nodes = '''
    LOAD CSV WITH HEADERS FROM 'file:///var/lib/neo4j/import/products_sellers.csv' AS product_line FIELDTERMINATOR '\u0001'
    // Create products
    MERGE (p:Product
                {product_id: product_line.product_id,
                 product_name: product_line.product_name,
                 category_name: product_line.product_category_name,
                 description: product_line.product_long_description
                 })
    '''
    create_properties_nodes = '''
    LOAD CSV WITH HEADERS FROM 'file:///var/lib/neo4j/import/products_properties.csv' AS property_line FIELDTERMINATOR '\u0001'
    // Create properties
    MERGE (:Property {
            property_value: property_line.property_value
    })
    '''

    create_sellers_nodes = '''
    LOAD CSV WITH HEADERS FROM 'file:///var/lib/neo4j/import/products_sellers.csv' AS seller_line FIELDTERMINATOR '\u0001'
    // Create sellers
    MERGE (:Seller {
            seller_id: seller_line.seller_id,
            seller_name: seller_line.seller_name
    })
    '''
    
    product_property_relationship = '''
    // Create a relationship between the products and properties
    CALL apoc.periodic.iterate(
      '
      LOAD CSV WITH HEADERS FROM "file:///var/lib/neo4j/import/products_properties.csv" AS line FIELDTERMINATOR "\u0001"
      RETURN line
      ',
      '
      MATCH (p:Product {product_id: line.product_id})
      MATCH (pr:Property {property_value: line.property_value})
      MERGE (p)-[:Has]->(pr)
      ',
      {batchSize: 5000, iterateList: true}
    )
    '''
    
    product_seller_relationship = '''
    // Create a relationship between the products and the sellers
    CALL apoc.periodic.iterate(
      '
      LOAD CSV WITH HEADERS FROM "file:///var/lib/neo4j/import/products_sellers.csv" AS line FIELDTERMINATOR "\u0001"
      RETURN line
      ',
      '
      MATCH (p:Product {product_id: line.product_id})
      MATCH (s:Seller {seller_id: line.seller_id})
      MERGE (s)-[:Sells]->(p)
      ',
      {batchSize: 5000, iterateList: true}
    )
    '''

    product_product_relationship = '''
    // Create a relationship between the products and properties
    CALL apoc.periodic.iterate(
      '
      LOAD CSV WITH HEADERS FROM "file:///var/lib/neo4j/import/product_product.csv" AS line FIELDTERMINATOR "\u0001"
      RETURN line
      ',
      '
      MATCH (p:Product {product_id: line.id})
      MATCH (neighbor:Product {product_id: line.neighbor_id})
      MERGE (p)-[:Neighbors]->(neighbor)
      MERGE (neighbor)-[:Neighbors]->(p)
      ',
      {batchSize: 5000, iterateList: true}
    )
    '''
    
    product_product_relationship_weighted = '''
    // Create a relationship between the products and properties
    CALL apoc.periodic.iterate(
      '
      LOAD CSV WITH HEADERS FROM "file:///var/lib/neo4j/import/product_product.csv" AS line FIELDTERMINATOR "\u0001"
      RETURN line
      ',
      '
      MATCH (p:Product {product_id: line.id})
      MATCH (neighbor:Product {product_id: line.neighbor_id})
      MERGE (p)-[r:Neighbors {weight: toFloat(line.distance)}]->(neighbor)
      MERGE (neighbor)-[:Neighbors {weight: toFloat(line.distance)}]->(p)
      ',
      {batchSize: 5000, iterateList: true}
    )
    '''
    
    with driver.session(database="neo4j") as session:
        if cleaning_before_pushing:
            session.execute_write(
                lambda tx: tx.run(cleaning_all).data())
            print("Cleaning done")
        if index:
            session.execute_write(
                lambda tx: tx.run(products_idx).data())
            session.execute_write(
                lambda tx: tx.run(property_idx).data())
            print("Indexes done")
        if nodes:
            session.execute_write(
                lambda tx: tx.run(create_products_nodes).data())
            print("Product nodes added")
            session.execute_write(
                lambda tx: tx.run(create_properties_nodes).data())
            print("Properties nodes added")
            session.execute_write(
                lambda tx: tx.run(create_sellers_nodes).data())
            print("Sellers nodes added")
        if relationship:
            session.execute_write(
                lambda tx: tx.run(product_property_relationship).data())
            print("product_property relationships added")
            session.execute_write(
                lambda tx: tx.run(product_seller_relationship).data())
            print("product_seller relationships added")
            if weighted_relationship:
                session.execute_write(
                    lambda tx: tx.run(product_product_relationship_weighted).data())
            else:
                session.execute_write(
                    lambda tx: tx.run(product_product_relationship).data())
            print("product_product relationships added")
    driver.close()
