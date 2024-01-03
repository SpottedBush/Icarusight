import numpy as np
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
    confusion_matrix,
    fowlkes_mallows_score,
)
from pyclustering.utils import calculate_distance_matrix
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.centrality import girvan_newman


def ultimate_measurement_tool(labels, measures_TODO, data=None, ground_truth_labels=None, printing=False):
    """Ground_truth_labels is the true cluster labels
    Labels is the predicted cluster labels
    Measures_TODO is a list of strings that tells which measures to do
    Checkout trashBin for original disgusting code if this doesn't works"""
    res = []
    metric_functions1 = {
        "silhouette": silhouette_score,
        "db_index": davies_bouldin_score,
        "ch_index": calinski_harabasz_score,
        "dunn_index": lambda data, labels: cluster_metrics.dunn(calculate_distance_matrix(data), labels),
    }
    metric_functions2 = {
        "ari": adjusted_rand_score,
        "nmi": normalized_mutual_info_score,
        "purity": lambda ground_truth_labels, labels: np.sum(
            np.max(confusion_matrix(ground_truth_labels, labels), axis=0)) / np.sum(
            confusion_matrix(ground_truth_labels, labels)),
        "fm_index": fowlkes_mallows_score,
    }

    for tool in measures_TODO:
        tool = tool.lower()
        if tool in metric_functions1:
            metric_function = metric_functions1[tool]
            metric_value = metric_function(data,
                                           labels) if data is not None and ground_truth_labels is not None else metric_function(
                labels)
            if printing:
                print(f"{tool.capitalize()}:", metric_value)
            res.append(metric_value)
        elif tool in metric_functions2:
            metric_function = metric_functions2[tool]
            metric_value = metric_function(ground_truth_labels,
                                           labels) if data is not None and ground_truth_labels is not None else metric_function(
                labels)
            if printing:
                print(f"{tool.capitalize()}:", metric_value)
            res.append(metric_value)

    return res


# Example usage:
# res = ultimate_measurement_tool(labels, ["silhouette", "db_index"], data=data, ground_truth_labels=ground_truth_labels, printing=True)


from mpl_toolkits.mplot3d import Axes3D

# Dictionary of clustering algorithms
clustering_algorithms = {
    "Louvain Community Detection": lambda graph: community.best_partition(graph),
    "Girvan-Newman Community Detection": girvan_newman,
    "Markov Clustering (MCL)": None,  # Requires the python-markov-clustering library
    "Label Propagation": lambda graph: list(
        nx.algorithms.community.label_propagation.label_propagation_communities(graph)),
    "Infomap": None,  # Requires the pyInfomap library or similar implementations
    "K-Clique Percolation": None,  # Custom implementation or third-party libraries
    "SCAN (Structural Clustering Algorithm for Networks)": None,  # Custom implementation or third-party libraries
    "Walktrap (Hierarchical)": lambda graph: nx.algorithms.community.centrality.asyn_fluidc(graph, 3),
    "Walktrap (Single-level)": lambda graph: nx.algorithms.community.community_utils.is_partition(graph,
                                                                                                  nx.algorithms.community.centrality.asyn_fluidc(
                                                                                                      graph, 3)),
}


def apply_single_algorithm(g, algorithm_name):
    algorithm_func = clustering_algorithms[algorithm_name]
    return algorithm_func(g)


def compare_all_algorithms(g):
    # Create subplots for 3D plots
    n_rows, n_cols = 2, 4
    fig = plt.figure(figsize=(15, 8))
    # Iterate over each clustering algorithm and plot the results
    for i, (name, algorithm) in enumerate(clustering_algorithms.items()):
        ax = fig.add_subplot(n_rows, n_cols, i + 1, projection='3d')  # Create a 3D subplot
        labels = algorithm.fit_predict(g)
        axis = np.array(g).T

        # Scatter plot in 3D
        ax.scatter(axis[0], axis[1], axis[2], c=labels, cmap='viridis')
        ax.set_title(name)

        # Set axis labels
        ax.set_xlabel("Product Category")
        ax.set_ylabel("Seller")
        ax.set_zlabel("Brand")

    plt.tight_layout()
    plt.show()
