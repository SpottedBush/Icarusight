import pandas as pd

from Icarusight.queries.getQueries import query_product_df, query_co_viewed_df
from Icarusight.Icarusight.utils import *
from Icarusight.Icarusight.flatXcoviewed_model.flatXcoviewed_model import create_flat_x_coviewed_graph
from Icarusight.Icarusight.flatXcoviewed_model.clustering import get_cluster_labels, apply_clustering_algorithm
from collections import Counter


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

    # Get the number of nodes in each cluster (i.e: the number of occurrences of each cluster_id)
    # cluster_counts = Counter(input_dict.values())
    # ids_to_keep = [value for value, count in cluster_counts.items() if count > n]
    # print(ids_to_keep)
    # filtered_dict = {}
    # for cluster_id in ids_to_keep:
    #     filtered_dict_tmp = dict(filter(lambda item: item[1] == cluster_id, input_dict.items()))
    #     print(filtered_dict_tmp)
    #     for item in filtered_dict_tmp.items():
    #         filtered_dict[item[0]] = item[1]
    #     print(filtered_dict)
    # return filtered_dict


print("Starting queries.", end="")
product_df = query_product_df()
print(".", end="")
co_viewed_df = query_co_viewed_df()
print(" Done, length of co_viewed is: ", len(co_viewed_df))

print("Starting graph creation")
g = create_flat_x_coviewed_graph(product_df, co_viewed_df)
print("Graph creation done.", end=" ")
print(f"got {len(g.nodes)} nodes and {len(g.edges)} edges.")

print("Starting clustering...")
partitions = apply_clustering_algorithm(g)
max_value_before = max(partitions.values(), key=lambda x: x)
print("Clustering done.")
partitions = remove_meaningless_clusters(partitions, n=3)
max_value_after = max(partitions.values(), key=lambda x: x)
print("before: ", max_value_before, "| after: ", max_value_after)
cluster_labels, cluster_max_values, cluster_total_len = get_cluster_labels(g, partitions)
print("Saving results...")
# save_results() ||  need to redefine save_results()
print("Results saved.")
