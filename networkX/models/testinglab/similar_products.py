import ssl
import nltk
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF

# def get_copurshased_products(product_name):
# TODO: get the co-purchased list (from maybe tracked enriched ?) and return it


# Similarities calculations part

tfidf_vectorizer = TfidfVectorizer(stop_words=nltk.corpus.stopwords.words('french'), max_features=1000)
tfidf_matrix = None
cosine_sim = None
svd = TruncatedSVD(n_components=500, random_state=42)


def define_cos_sim(df, debug_mode=False):
    """
    Define the tfidf matrix and the cosine similarity based on the product_long_description.
    @param df: Dataframe from which the column product_long_description will be extract
    @type df: pandas.core.frame.DataFrame
    @param debug_mode: Activate or deactivate debug mode
    @type debug_mode: bool
    """
    global cosine_sim, tfidf_matrix
    if tfidf_matrix is None or cosine_sim is None:
        tfidf_matrix = tfidf_vectorizer.fit_transform(df["product_long_description"])
        svd.fit(tfidf_matrix)
        if debug_mode:
            print(svd.explained_variance_ratio_)
            svd_cumsum = svd.explained_variance_ratio_.cumsum()
            print(svd_cumsum)
            print(svd.singular_values_)
            print(tfidf_matrix.shape)
            plt.plot(svd_cumsum, xlabel="explained variance", ylabel="number of components")
            plt.show()

        # Compute cosine similarity
        tfidf_matrix = svd.transform(tfidf_matrix)  # Perform dimensionality reduction on tfidf_matrix
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


def get_related_products(df, product_name, need_update=False):
    """
    Get related products based on their semantic similarity.
    @param df: The dataframe to extract features from
    @type df: pandas.core.frame.DataFrame
    @param product_name: Name
    @type product_name: str
    @param need_update: If put at True download the latest nltk dictionary (stopwords and punkt)
    @type need_update: bool
    @return:
    @rtype:
    """
    if tfidf_matrix is None or cosine_sim is None:
        define_cos_sim(df)
    if need_update == 1:
        ssl._create_default_https_context = ssl._create_unverified_context
        nltk.download('punkt')
        nltk.download('stopwords')
    if len(df[df['product_name'] == product_name]) == 0:
        return []

    product_idx = df[df['product_name'] == product_name].index[0]
    similar_scores = list(enumerate(cosine_sim[product_idx]))
    similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)
    similar_scores = similar_scores[1:]  # Exclude the product itself, even tho it is related to itself
    for i in range(len(similar_scores)):
        if similar_scores[i][1] < 0.70:
            similar_scores = similar_scores[:i]
            break
    return [(j[0], df.iloc[j[0]]) for j in similar_scores]
