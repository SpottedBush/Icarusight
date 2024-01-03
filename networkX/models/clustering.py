import pandas as pd
import networkx as nx
from Icarusight.Icarusight.utils import *
from community import community_louvain
import networkx.algorithms.community as nx_comm
from collections import defaultdict
from tqdm import tqdm


def apply_clustering_algorithm(graph, clustering_algorithm="Louvain"):
    """
    Apply a clustering algorithm to a graph between those:
    - Louvain (Louvain=default)
    - Label Propagation (LP)
    - Weakly Composed Components (WCC)
    - Triangle Count (TC)
    - Local Clustering Coefficient (LCC)
    - K-Core Decomposition (KCD)
    - K-1 Coloring (K1C)
    - Modularity Optimization (MO)
    - Strongly Connected Components (SCC)
    - Speaker-Listener Label Propagation (SLLP)
    - Approximate Maximum K-Cut (AMKC)
    - Conductance Metric (CM)
    - Modularity Metric (MM)
    - K-Means Clustering (KMC)
    - Leiden (Leiden)
    @param graph: The Networkx graph to which apply the clustering algorithm
    @type graph: networkx.classes.graph.Graph
    @param clustering_algorithm: The name of the clustering algorithm to apply, use the corresponding acronym given in the description to chose one.
    For example if you want to use Conductance Metric, please write CM
    @type clustering_algorithm: str
    @return: The partitions of the corresponding clustering algorithm under the following form: {node_name: cluster_id}
    @rtype: dict[str,str]
    """
    if clustering_algorithm == "Louvain":
        return community_louvain.best_partition(graph)

    # elif clustering_algorithm == "LP":
    #     label_prop = LabelPropagation()
    #     label_prop.fit(graph)
    #     labels = label_prop.labels_
    #     return {str(node): str(label) for node, label in enumerate(labels)}

    elif clustering_algorithm == "WCC":
        components = list(nx.weakly_connected_components(graph))
        return {node: component_id for component_id, component in enumerate(components) for node in component}

    elif clustering_algorithm == "TC":
        triangles = nx.triangles(graph)
        return {node: str(triangles[node]) for node in graph.nodes()}

    elif clustering_algorithm == "LCC":
        local_clustering_coef = nx.clustering(graph)
        return {node: str(local_clustering_coef[node]) for node in graph.nodes()}

    elif clustering_algorithm == "KCD":
        k_core = nx.core_number(graph)
        return {node: str(k_core[node]) for node in graph.nodes()}

    elif clustering_algorithm == "K1C":
        coloring = nx.coloring.greedy_color(graph, strategy="largest_first")
        return {node: str(color) for node, color in coloring.items()}

    elif clustering_algorithm == "MO":
        communities = list(nx_comm.greedy_modularity_communities(graph))
        cluster_dict = {}
        for idx, community in enumerate(communities):
            for node in community:
                cluster_dict[node] = str(idx)
        return cluster_dict

    elif clustering_algorithm == "SCC":
        scc = list(nx.strongly_connected_components(graph))
        return {node: component_id for component_id, component in enumerate(scc) for node in component}

    elif clustering_algorithm == "SLLP":
        # Implement SLLP here
        print("Not yet implemented!")
        pass

    elif clustering_algorithm == "AMKC":
        # Implement AMKC here
        print("Not yet implemented!")

        pass

    elif clustering_algorithm == "CM":
        # Implement Conductance Metric here
        print("Not yet implemented!")
        pass

    elif clustering_algorithm == "MM":
        # Implement Modularity Metric here
        print("Not yet implemented!")
        pass

    elif clustering_algorithm == "KMC":
        # Implement K-Means Clustering here
        print("Not yet implemented!")
        pass

    elif clustering_algorithm == "Leiden":
        # Implement Leiden here
        print("Not yet implemented!")
        pass

    else:
        raise ValueError("Invalid clustering algorithm specified.")


def get_cluster_labels(g, partitions):
    """
    Obtains the main category, the sum of the nodes having that category, and the total number of nodes in each cluster.
    @param g: The Networkx graph to apply the clustering algorithm
    @type g: networkx.classes.graph.Graph
    @param partitions: Partitions must be under the following form: {node_name: cluster_id}
    @type partitions: dict[str, str]
    @return: ([cluster_id: Main category], [cluster_id: Number of nodes having the main category], [cluster_id: Total number of nodes])
    @rtype:  tuple[dict[str, str], dict[str, int], dict[str, int]]
    """
    # Create dictionaries to store cluster category counts, main labels, max values, and summed values.
    cluster_categories = defaultdict(lambda: defaultdict(int))
    cluster_main_labels = {}
    cluster_max_value = {}
    cluster_summed_values = {}

    # Iterate through the partitions and group nodes by cluster_id
    for node_name, cluster_id in tqdm(partitions.items(), total=len(partitions.items())):
        node_category = get_node_feature(g, node_name, 'category')
        if node_category:
            category_name = categories_mapping.get(node_category)
            if category_name:
                cluster_categories[cluster_id][category_name] += 1

    # Get the most common category for each cluster, max value, and summed value
    for cluster_id, category_counts in tqdm(cluster_categories.items(), total=len(cluster_categories.items())):
        if category_counts:
            max_category = max(category_counts, key=category_counts.get)
            max_value = category_counts[max_category]
            total_nodes = sum(category_counts.values())
            cluster_main_labels[cluster_id] = max_category
            cluster_max_value[cluster_id] = max_value
            cluster_summed_values[cluster_id] = total_nodes
        else:
            cluster_main_labels[cluster_id] = None

    return cluster_main_labels, cluster_max_value, cluster_summed_values


def get_node_feature(g, node_name, feature):
    """
    Get the attributes of a node
    @param g: A Networkx graph
    @type g: networkx.classes.graph.Graph
    @param node_name: Name of the node in the graph
    @type node_name: str
    @param feature: Name of the attribute you want to get
    @type feature: str
    @return: The id of the feature (through the feature_mapping dict)
    @rtype: int
    """
    return nx.get_node_attributes(g, feature)[node_name]


def remove_meaningless_clusters(input_dict, n):
    """
    Reduce the number of clusters by removing the meaningless ones.
    @param input_dict: Corresponds to the output partitions from the clustering algorithm under the form {node_id:cluster_id}
    @type input_dict: dict[str:str]
    @param n: Filter the clusters on their number of nodes in it. Keeps only the clusters with more than n nodes.
    @type n: int
    @return: Returns the input_dict without the meaningless nodes (i.e: clusters)
    @rtype: dict[str:str]
    """
    df = pd.DataFrame({"node_id": input_dict.keys(), "cluster_id": input_dict.values()})
    count_df = df.groupby("cluster_id", as_index=False).size()
    count_df = count_df.loc[lambda x: x["size"] > n]  # Filtering by size > n
    df = df.merge(right=count_df.drop(columns=["size"]), how="inner", on="cluster_id")
    return {node_id: cluster_id for node_id, cluster_id in df.itertuples(index=False)}
