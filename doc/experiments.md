## Protocol
The icarusight project follows a very simple protocol that changes very little between its different versions. The base protocol is the following: <br />
- Querying Snowflake and storing all the required data into Pandas dataframes.
- Creating a graph for it -> nodes and edges (check appendix part for the detailed Neo4j pipeline).
- Applying Louvain's community detection algorithm.
- Group by community and analyze those communities.


The relationship `Neighbors` is obtained by using ANNOY on the embeddings of titles + descriptions of our Products (c.f. The neo4j pipeline figure in appendix part) and searching for the k(=10) nearest neighbors
<br />
## Modelisations
### Networkx
- **Co-viewed Model:**
  - Node: Products
  - Edge: (Product A)<-[Viewed With]->(Product B)
 <br /> <br />

- **Multi-Nodes Model:**
  - 2 Types of nodes:
    - Products
    - Properties
  - Edge: (Product)<-[Has]->(Property)
 <br /> <br />

- **Products_only Model (Binary):**
  - Node: Properties
  - Edge: (Product)-[Neighbors]->(Product)
 <br /> <br />

### Neo4j
- **Co-viewed Model:**
  - Node: Products
  - Edge: (Product A)<-[Viewed With]->(Product B):
 <br /> <br />

- **Products_only Model (Binary):**
  - Node: Products
  - Edge: (Product)-[Neighbors]->(Product)
 <br /> <br />

- **Products_only Model (Weighted):**
  - Node: Properties
  - Edge: (Product)-[Neighbors]->(Product) {Weight: Cosine similarity distances between the two products's titles and descriptions and then normalized with a min-max normalization.}
 <br /> <br />

- **Multi-Nodes, Multi-Edges Model:**
  - 3 Types of nodes: 
    - Products
    - Properties
    - Sellers
  - 3 Types of edges:
    - (Product)-[Has]->(Properties)
    - (Product)-[Neighbors]->(Neighbor)
    - (Seller)-[Sells]->(Product)
 <br />

####***Legend:***
- {Weight: What is the weight corresponding to}: The relationships are binary unless weight is precised.
- Product: Cdiscount product that belongs to the "Canapés - Housses de canapé" categories and has an offer score above D.
- Property: Property from the perimeter. ("Canapé - Housses de canapé" categories)
- Seller: Seller having one of his products in our perimeter.
- (Product A)<-[Viewed With]->(Product B): Products viewed in a single LR
- (Product)<-[Has]->(Property): Product has a certain property (We tried making this relationship weighted but the volume of data was too big, thus we moved to Neo4j)
- (Seller)-[Sells]->(Product): Seller sells product


## Observations:
For Networkx modelisations, as explained before, our goal was a bit different thus we'll keep our observations short.<br />
For the protocol we built our graph, then applied Louvain's community detection algorithm and then did topic modeling using TF-IDF and CountVectorizer on products's titles and descriptions
- Co-viewed Model: Highlights products belonging to the same Cdiscount category
- Multi-Nodes Model: Highlights products having the same properties.
For Neo4j modelisations the protocol follows the pipeline in the appendix (figure 1):
- Co-viewed Model: Highlights products belonging to the same Cdiscount category (Reproducing Networkx's Co-viewed model)<br />

- Products_only Model (Binary): We get good groups of "variants / doubloons", but isn't systemic, even with cutoffs applied to tf-idf there isn't much we can do.<br />

- Products_only Model (Weighted): So far our best model to get doubloons. <br />
  The main hyperparameter we have is the number of nearest neighbors for each product. <br /> 
  Then we use the cosine similarity distances (aka means, quantils (5%, 25%, 95%)) to define cutoffs in order to know wether a community is containing doubloons or not. <br />

- Multi-Nodes, Multi-Edges Model: That model is containing a lot of noise and did not bring much insight. By far the worse results we obtained.

## Possible improvements:
- Play with the hyperparameters like the number of neighbors (k), or the cutoff you want to apply.
- Trying other community detection algorithms (we tried some, but none were really fitting our use case so we stayed on Louvain's community detection algorithm).



## Appendix
![plot](/img/pipeline_neo4j.png)
*Figure 1: Pipeline for Neo4j's workflow*