import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pyvis.network import Network

# Function to load JSON data from a file
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to preprocess and normalize the data
def preprocess_data(data):
    # Normalize nested columns like 'colors'
    df = pd.json_normalize(data, max_level=1, sep='_', errors='ignore')
    
    # Drop the 'variant' column
    if 'variant' in df.columns:
        df = df.drop(columns=['variant'])
    
    return df
# Function to get tag frequencies
def get_tag_frequencies(df):
    tags_series = df["tags"].explode().dropna()
    tag_counts = tags_series.apply(lambda x: x['tag_slug']).value_counts()
    return tag_counts


def data_visualization():
    # Streamlit app
    st.subheader("Data Source Visualization")

    # Load data from JSON file
    data_file = "souled_store_products.json"
    data = load_data(data_file)

    # Preprocess and normalize the data
    df = preprocess_data(data)

    # Display whole dataset
    st.write("## Full Dataset")
    st.write(df)

    # Visualizations
    st.write("## Visualizations")

    # Example visualizations
    # Bar chart for prices
    st.write("### Price Distribution")
    st.bar_chart(df["price"])

    # Line chart for average ratings
    st.write("### Average Rating Over Products")
    st.line_chart(df["avg_rating"])

    # Area chart for rating count
    st.write("### Rating Count Over Products")
    st.area_chart(df["rating_count"])

    # Table for available colors with counts
    st.write("### Available Colors")
    colors_series = df["colors"].explode().dropna()
    colors_df = pd.json_normalize(colors_series)
    unique_colors = colors_df.groupby("color_name").size().reset_index(name='count')
    sorted_unique_colors = unique_colors.sort_values(by='count', ascending=False)
    st.table(sorted_unique_colors.set_index("color_name"))

    # Graph-type visualization for tags
    st.write("### Tag Frequencies")
    tag_counts = get_tag_frequencies(df)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=tag_counts.index, y=[1]*len(tag_counts), size=tag_counts.values, sizes=(50, 500), legend=False)
    plt.title("Tag Frequencies")
    plt.xlabel("Tag")
    plt.ylabel("Size proportional to Frequency")
    plt.xticks(rotation=45, ha='right')
    st.pyplot()

    # Display tag counts as table
    st.write("### Tag Counts")
    st.table(tag_counts.reset_index().rename(columns={"index": "Tag Slug", "tags": "Count"}))
