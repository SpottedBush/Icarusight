import re
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
from pyvis.network import Network
import spacy

categories_mapping = {}
sellers_mapping = {}
brands_mapping = {}
colors_mapping = {}

# Contains name:id
name_mapping = {}


def str2value_mapping(input_string, mapping_dict):
    """
    One hot encoder, turns the entry string into its corresponding id if it exists else it creates an id for it and returns the id
    @param input_string: The string to encode
    @type input_string: str
    @param mapping_dict: Dictionary that will contain the input string under the form {id:input_string}
    @type mapping_dict: dict[int,str]
    @return: The corresponding id
    @rtype: int
    """
    if input_string in mapping_dict.values():
        # If the string already exists in the dictionary, return its associated ID
        return list(mapping_dict.keys())[list(mapping_dict.values()).index(input_string)]
    else:
        # If the string doesn't exist, create a new ID for it and add it to the dictionary
        new_id = len(mapping_dict) + 1
        mapping_dict[new_id] = input_string
        return new_id


def refined_str(input_string):
    """
    Remove quotes, and sum up the sellers aggregate entry under the form '"seller1","seller2"...'
    @param input_string: String to clean
    @type input_string: str
    @return: List containing the sellers name in the same order as the input string
    @rtype: list
    """
    result = []
    inside_quotes = False
    current_string = ""

    for char in input_string:
        if char == '"':
            if inside_quotes:
                result.append(current_string)
                current_string = ""
            inside_quotes = not inside_quotes
        elif inside_quotes:
            current_string += char
    return result


def df2features(df, i):
    """
    Takes the row i from the dataframe and turn it into a feature dictionary
    @param df: The dataframe to extract features from
    @type df: pandas.core.frame.DataFrame
    @param i: The index corresponding to the row you want to extract the features from
    @type i: int
    @return: A dictionary containing the features
    @rtype: dict[str,int]
    """
    return {'product_id': df['product_id'][i],
            'category_id': str2value_mapping(df['product_category_name'][i], categories_mapping),
            'sellers': refined_str(df['seller_names'][i]),
            'brand_id': str2value_mapping(df['brand_name'][i], brands_mapping),
            'name_id': str2value_mapping(df['product_name'][i], name_mapping),
            'description': df['product_long_description'][i]
            }


nlp = spacy.load('fr_core_news_md')


def cleaning_strings(original_string, use_lemma=False):
    """
    Processing strings by removing :
    - & followed by digits.
    - non-alphanumeric chars and spaces.
    - double spaces.\n
    Then apply lemmatization (if use_lemma is set to true)
    @param original_string: The input string to clean
    @type original_string: str
    @param use_lemma: Whether lemma should be used or not
    @type use_lemma: bool
    @return: The string cleaned
    @rtype: str
    """
    # Delete "&" followed by digits
    cleaned_string = re.sub(r'^&\d+', '', original_string)

    cleaned_string = re.sub(r'^\(.*\)', '', cleaned_string)
    # Delete non-alphanumeric chars and spaces
    cleaned_string = re.sub(r'[^a-zA-Z0-9À-ÖØ-öø-ÿĀ-ž]', ' ', cleaned_string)
    # double spaces
    cleaned_string = ' '.join(cleaned_string.split())
    if use_lemma:
        doc = nlp(cleaned_string)
        res_str = ""
        for token in doc:
            res_str += token.lemma_ + " "

        return res_str
    return cleaned_string


def write_html_from_nx(g, html_path):
    """
    Save a graph to an html file
    @param g: The graph to save in the html file
    @type g: networkx.classes.graph.Graph
    @param html_path: The path where the html file will be saved
    @type html_path: str
    """
    # Creating the pyvis graph
    nt = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    nt.from_nx(g)
    nt.set_options(
        """{
            "physics": {
                "maxVelocity": 15,
                "minVelocity": 0.75
            }
        }"""
    )
    nt.save_graph(html_path)
    print("Graph saved!")
