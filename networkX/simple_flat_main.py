from Icarusight.Icarusight.utils import *
from Icarusight.flat import create_flat_graph
import networkx as nx
from cdiscount import config
from cdiscount import snowflake
from community import community_louvain
import gravis as gv
from tqdm import tqdm
import concurrent.futures


# This was meant for flat-ish property comparison graph, but it is now useless

def refined_strings_df(df, categories):
    for category in categories:
        df[category] = df[category].apply(cleaning_strings)


def create_clustered_graph(graph):
    """
    Apply clustering on a graph and then create another based upon the first one
    @param graph: The input graph to apply clustering on
    @type graph:
    @return:
    @rtype:
    """
    partition = community_louvain.best_partition(graph)
    print("Clustering done")
    communities = {}
    for node, community in partition.items():
        if community not in communities:
            communities[community] = [node]
        else:
            communities[community].append(node)
    print("Creating clustered graph")

    def add_edges_to_community(community_id, nodes):
        subgraph = nx.Graph()
        subgraph.add_nodes_from(nodes)
        for node1 in nodes:
            for node2 in nodes:
                if node1 != node2:
                    subgraph.add_edge(node1, node2)
        return community_id, subgraph

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(add_edges_to_community, communities.keys(), communities.values()))

    community_graph = nx.Graph()
    for community_id, subgraph in tqdm(results, total=len(results)):
        community_graph.add_nodes_from(subgraph.nodes)
        community_graph.add_edges_from(subgraph.edges)

    return community_graph


secrets = config.load_secrets('queries/mes-secrets.yml', key='snowflake')
product_property_comparison_query_path = "queries/GetProductComparison_WHOLE.sql"
print("Starting query")
with snowflake.get_snowflake_connection(**secrets) as con:
    comparison_df = snowflake.query_snowflake_to_df(product_property_comparison_query_path, con=con)
    categories_to_refine = ['first_product_name', 'first_product_category_name', 'first_product_description',
                            'second_product_name', 'second_product_category_name', 'second_product_description']
    refined_strings_df(df=comparison_df, categories=categories_to_refine)
    print("Query and refining strings done, starting graph creation.")
g = create_flat_graph(comparison_df)
print("Graph creation done, starting clustering.")
clustered_graph = create_clustered_graph(g)

print("Saving the results...")
write_html_from_nx(clustered_graph, "/data2/dashboards/pyvis_graphs/nx_clustered.html")
print("nx done")
fig1 = gv.vis(g, show_node_label=False, show_edge_label=False)
fig1.export_html("/data2/dashboards/gravis_graphs/non_clustered.html")
print("Gravis halfway done")
fig = gv.vis(clustered_graph, show_node_label=False, show_edge_label=False)
fig.export_html("/data2/dashboards/gravis_graphs/clustered.html")
print("Clustering done and saved!")
