from Icarusight.Icarusight.utils import *
import networkx as nx
from tqdm import tqdm


def add_product_node(g, product_id, features):
    """
    Add a node to the graph with its features
    @param g: The Networkx graph where you'll add the node
    @type g: networkx.classes.graph.Graph
    @param product_id: The id of the node
    @type product_id: str
    @param features: A dictionary containing your node's attributes
    @type features: dict[str:int]
    """
    g.add_node(product_id, category=features['category_id'],
               brand=features['brand_id'],
               name=features['name_id'],
               description=features['description'],
               type="product")


def add_property_node(g, property_id, features):
    """
    Add a node to the graph with its features
    @param g: The Networkx graph where you'll add the node
    @type g: networkx.classes.graph.Graph
    @param product_id: The id of the node
    @type product_id: str
    @param features: A dictionary containing your node's attributes
    @type features: dict[str:int]
    """
    g.add_node(property_id,
               type="property")


def create_multi_node_graph(product_df, property_df):
    """
    In this graph model there are 2 types of nodes : products and properties (name + value).
    Products nodes are linked to properties when they have it
    @param product_df: The dataframe containing the products and their infos.
    @type product_df: pandas.core.frame.DataFrame
    @param property_df: The dataframe containing the properties and a list of products containing it.
    @type property_df: pandas.core.frame.DataFrame
    @return: the Networkx graph corresponding to your dataframes
    @rtype: networkx.classes.graph.Graph
    """
    g = nx.Graph()
    num_nodes = len(product_df)
    print("Adding nodes...")
    for i in tqdm(range(num_nodes), total=num_nodes):
        product_id = df['product_id'][i]
        row = df2features(df, i)
        add_product_node(g, product_id, row)

    # Add edges for co-viewed products
    print("Nodes added, adding edges...")
    num_edges = len(co_viewed_df)
    for i in tqdm(range(num_edges), total=num_edges):
        g.add_edge(co_viewed_df['ref_id'][i], co_viewed_df['related_id'][i], relation="Co-vus",
                   color='purple')
    print("Edges added.")
    return g
