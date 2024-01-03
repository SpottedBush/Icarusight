import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('french'))


def preprocess_text(text):
    """
    Preprocess the input text into lowercase, remove stop words and remove non-alphabetic words
    @param text: String to preprocess
    @type text: str
    @return: The processed text
    @rtype: str
    """
    words = word_tokenize(text.lower(), language='french')
    words = [word for word in words if word.isalpha() and word not in stop_words]
    return ' '.join(words)


def find_dominant_words(descriptions):
    """
    Process the descriptions using the TF-IDF and NMF.
    Text analysis and topic modeling are done.
    @param descriptions: Descriptions from which you'll set the matrices
    @type descriptions: list[str]
    @return: String containing the main keywords
    @rtype: str
    """
    preprocessed_descriptions = [preprocess_text(desc) for desc in descriptions]

    # Text Analysis (TF-IDF)
    tfidf_vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(preprocessed_descriptions)

    # Topic Modeling (NMF)
    num_topics = 2
    nmf_model = NMF(n_components=num_topics)
    nmf_matrix = nmf_model.fit_transform(tfidf_matrix)

    # Get the most important words for each topic
    feature_names = tfidf_vectorizer.get_feature_names_out()
    top_words_per_topic = []
    for topic_idx, topic in enumerate(nmf_model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-5 - 1:-1]]
        top_words_per_topic.append(top_words)

    # After NMF modeling, identify the dominant topic for each description
    dominant_topics = [topic.argmax() for topic in nmf_matrix]
    main_theme_topic = max(set(dominant_topics), key=dominant_topics.count)

    # Extract key phrase for the main theme
    main_theme_key_phrase = ', '.join(top_words_per_topic[main_theme_topic])

    print("Main Theme Key Phrase:", main_theme_key_phrase)
    return main_theme_key_phrase
