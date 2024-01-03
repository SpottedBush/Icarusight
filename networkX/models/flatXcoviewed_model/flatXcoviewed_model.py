from Icarusight.Icarusight.utils import *
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
               type=0, color='red')


def co_viewed_df_processing(g, co_viewed_df, product_id):
    """
    Process the co-viewed dataframe entry to add the edges between your node (product_id) and its co-viewed products
    @param g: The Networkx graph where you'll add the edges
    @type g: networkx.classes.graph.Graph
    @param co_viewed_df: coviewed_df based on the pilot DB
    @type co_viewed_df: pandas.core.frame.DataFrame
    @param product_id: The id of the node
    @type product_id: str
    """
    for j in range(len(co_viewed_df)):
        # co_view_count = int(co_viewed_df['couple_view_count'][j])
        # avoid making an edge from the node to the node itself
        if co_viewed_df['ref_id'][j] != product_id:
            continue
        related_product_id = co_viewed_df['related_id'][j]
        if not g.has_node(co_viewed_df['related_id'][j]):
            print('Something is wrong, missing node:', co_viewed_df['related_id'][j],
                  co_viewed_df['related_name'][j])
        g.add_edge(product_id, related_product_id, relation="Co-vus",
                   color='purple')


def create_flat_x_coviewed_graph(df, co_viewed_df):
    """
    Creates a graph with nodes being products that are linked when viewed together (co-viewed)
    @param df: product_df based on the pilot DB
    @type df: pandas.core.frame.DataFrame
    @param co_viewed_df: coviewed_df based on the pilot DB
    @type co_viewed_df: pandas.core.frame.DataFrame
    @return: the Networkx graph corresponding to your dataframes
    @rtype: networkx.classes.graph.Graph
    """
    g = nx.Graph()
    num_nodes = len(df)
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
