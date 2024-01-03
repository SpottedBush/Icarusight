## Context:
The icarusight project wasn't designed at first to detect doubloons thus the first metrics used were mainly graph geometrics, visuals (using for example Graphviz)
and tried some topic modeling with a custom TF-IDF and CountVectorizer.
Then for detecting doubloons few measurements were made:

## In general:
### Number of communities
The number of distinct communities formed from the community detection algorithm
### Community size
The number of nodes having the same community_id
### Top TF-IDF and CountVectorizer words 
Based on the title and description of each products belonging to the same community, applied TF-IDF and CountVectorizer to get the main words of each communities. 
### Density
Defined by: 
$$ density = \frac{number\:of\:edges}{community\:size \times 10} $$
Multiplying by 10 because we took the 10 closest neighbors (thus making 10 edges for each nodes at maximum)
### Distances
- Mean
- Quantils (5%, 25%, 95%)
- Median

## For LR specific purposes:
### avg_number_by_community
For a specific search_id it represents the average number of products by community contained in this LR (search_id), it is calculated by: <br />
$$ avg\_number\_by\_community = \frac{number\:of\:products}{number\:of\:community} $$
### main_lr_community
For a specific search_id it is the community that appears the most.
### n_obs
Number of products in a search_id.
### n_conv
Number of products in a search_id that belongs to the main community.
### rate
$$ rate = \frac{n\_conv}{n\_obs} $$
From this rate we also have those related metrics:
- rate_q1
- rate_mean
- rate_median
### n_pairs
Number of pairs contained in a search_id.
### q
Mean of the distances contained in a search_id.
### top_community_id_list
List of community_id that appears the most in a search_id.