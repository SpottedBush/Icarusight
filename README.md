# Icarusight

![plot](./img/Icarusight_logo2.png)

## Introduction

Welcome to the Icarusight project!
This project presents an innovative approach to representing the Cdiscount retail catalog as a graph.
We have explored two different tools: Networkx and Neo4j to model and analyze the catalog data, each having distinct pros and cons within the project.
To get the full grasp of how this works, check out the `doc` folder.
<br /> <br />
N.B: Icarusight's goal has changed since its starting point and now aims to detect doubloons or very similar products (such as variants).


## Context:
At the beginning (when using Networkx) we weren't sure about our goal with those modelisations, it could be used to associate clients's macro-needs and lists of products or to recategorize products.
In the end this project's goal is doubloons detection. Here the limit between similar products and doubloons is pretty blurry.


## LR Considerations
After detecting doubloons, another idea that we got was trying to find a quality index for LR (Research List => A list of products corresponding to a search_id). This index would highlight how different products are.
Suggestions were to apply the pipeline to short_tail and long_tail LRs (Was done only with Neo4j), the results weren't really significative.
We then tried to find an index without any graph modelisation (corresponding notebook name is `LR_index_without_graph`). <br />
The results were pretty interesting: as the average similarity in a search_id gets higher, the quantity of doubloons rises.
This means that getting a quality index for LRs can be done without graphs, with only cosine similarity and semantic distances (title and description taken into account). <br /> <br />
All the experimentations and results can be found in the lr folder.


## Important Notes

In this repository, you will find three folders, two of them are experimentations using different graph modeling tools; Networkx and Neo4j and the last one `doubloons_detection`
contains the best model, which uses Networkx. 
The two tools are used for different use cases within the project:

### Networkx

Networkx focuses on a micro-level view of the graph, considering individual nodes and their relationships. 
It was the initial tool used in this project, and many models have been tested with it.
Networkx is efficient and allows for quick development, but it has limitations in terms of the amount of data that can be stored in RAM. 
As the project progressed, we encountered limitations, which led us to explore Neo4j as an alternative solution.

### Neo4j

Neo4j takes a macro-level approach to graph modeling, focusing on classes of nodes and their relationships. 
It uses the Cypher language, similar to SQL, for querying and interacting with the created graphs. 
In this project, we have exclusively used Neo4j with sandbox-based databases.
This approach provides the scalability and performance needed for handling larger datasets.
There is a downside though : at this date it is not usable in a job.

### doubloons_detection
That folder isn't containing much: 
- **queries:** All the queries used for getting data from Snowflake. Stored in separate sql files.
- **results:** All csv or data produced by the notebook goes here.
- **custom_tf_idf_class.py:** A fine tuned TF-IDF class for this use case.
- **doubloons_community_detection.ipynb:** Notebook containing the strict minimum to get the communities of doubloons. It can be segmented in different part:
  - **GET EMBEDDINGS AND PRODUCTS_DF** -> Produces the dataframes needed for the notebook. It uses Snowflake, be aware that you have to change the credentials in secret.yml.
  - **ANNOY(ING) NEIGHBORS** -> Uses the embeddings to create a tree and get the semantic distances between products.
  - **COMMUNITY ANALYSIS** -> Applies the community detection algorithm and produce an analysis of those communities.
    - look4one_community(community_id): Get a grasp of a single community with its id.


## Getting Started

To get started with Icarusight, follow the instructions specific to each tool:

### Networkx

- **Requirements:** To work with Networkx, you need to install the required Python packages. You can do this by running the following command: `pip install -r requirements.txt`

### Neo4j

- **Running Locally:** We ran the Neo4j part of the project on Cdiscount's sandbox a08datasc002. To run it locally, we recommend using Docker.

- **Docker Image:** If the Neo4j Docker image is not already built, you can use the provided script, `neo4j/dockerrun`, to pull the Neo4j Docker image and run it with the right configurations.

- **Credentials:** You can access the Neo4j instance using the credentials specified in the `dockerrun` script, under the form `--env NEO4J_AUTH=$(user)/$(password)`.

- **Accessing Neo4j's endpoint:** Once the Neo4j Docker image is running, you can access the Neo4j endpoint using the following URL (note that you need to be on the Cdiscount namespace):

[http://a08datasc002.cdbdx.biz:7474/browser/](http://a08datasc002.cdbdx.biz:7474/browser/)

If you have any questions or need further assistance, please refer to the project's documentation or feel free to reach out to the project maintainers.
