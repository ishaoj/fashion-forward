import streamlit as st
import pickle
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
from utility.EmbeddingData import perform_embedding_operations
from utility.GenerateDesign import generate_combined_prompt
from utility.DataVisualization import data_visualization
import json
from PIL import Image
import io
import requests

from sklearn.impute import SimpleImputer

# Add this function to your code
def preprocess_features(features):
    imputer = SimpleImputer(strategy='mean')
    return imputer.fit_transform(features)

def load_product_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data
# Function to load combined features from pickle file
def load_combined_features(file_path):
    with open(file_path, 'rb') as f:
        combined_features = pickle.load(f)
    return combined_features

# Function for KMeans clustering
def perform_clustering(features, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features)
    return clusters, kmeans.cluster_centers_

def send_generation_request(host, params):
    STABILITY_KEY = "sk-zNscPJ92Re8yxG2QCw4b16qBJEj0JolkhDAvr8vkZwXl8USH"
    headers = {
        "Accept": "image/*",
        "Authorization": f"Bearer {STABILITY_KEY}"
    }

    files = {}
    image = params.pop("image", None)
    mask = params.pop("mask", None)
    if image is not None and image != '':
        files["image"] = open(image, 'rb')
    if mask is not None and mask != '':
        files["mask"] = open(mask, 'rb')
    if len(files) == 0:
        files["none"] = ''

    response = requests.post(
        host,
        headers=headers,
        files=files,
        data=params
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    return response

def generate_image(prompt):
    STABILITY_KEY = "sk-zNscPJ92Re8yxG2QCw4b16qBJEj0JolkhDAvr8vkZwXl8USH"  # Add your Stability API key here
    host = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    
    params = {
        "prompt": prompt,
        "negative_prompt": "",
        "aspect_ratio": "3:2",
        "seed": 0,
        "output_format": "png"
    }

    response = send_generation_request(host, params)

    output_image = response.content
    finish_reason = response.headers.get("finish-reason")
    seed = response.headers.get("seed")

    if finish_reason == 'CONTENT_FILTERED':
        raise Warning("Generation failed NSFW classifier")

    return output_image, seed

def main():
    st.title('Welcome to the Gen Z Fashion Trend Analyzer')

    # Initialize session state
    if 'cached_clusters' not in st.session_state:
        st.session_state.cached_clusters = None
    if 'cached_cluster_centers' not in st.session_state:
        st.session_state.cached_cluster_centers = None
    if 'combined_features' not in st.session_state:
        st.session_state.combined_features = None

    # Navigation sidebar
    page = st.sidebar.radio("Go to", ('Home','Data Visualition', 'Embedding Operations', 'Clustering', 'Prompt Generation'))

    if page == 'Home':
        
        st.subheader("The Challenge")
        st.write("""
        The fashion industry faces several challenges in capturing and responding to Gen Z trends:
        - **Rapid Trend Changes:** Gen Z fashion evolves at lightning speed across diverse social media platforms.
        - **Limited Data Integration:** Existing tools often analyze visuals and text separately, hindering comprehensive trend understanding.
        - **Personalization Gap:** Brands struggle to balance personalized experiences with mass-market production.
        - **Design Iteration Bottleneck:** There's a gap between trend identification and actionable design concepts.
        - **Unquantified Influencer Impact:** The influence of social media personalities on Gen Z fashion choices remains largely unmeasured.
        """)

        st.subheader("Our Solution")
        st.write("""
        We're revolutionizing Gen Z fashion trend analysis with cutting-edge AI:
        
        1. **Real-Time Trend Detection:** 
           - Continuous scraping of popular fashion blogs
           - CLIP analysis for instant trend identification
        
        2. **Narrative Behind the Look:** 
           - Combining CLIP's image understanding with GPT-3.5/4 text analysis
           - Unveiling the context and inspiration behind trending styles
        
        3. **Personalized Trend Targeting:** 
           - ML-powered segmentation of Gen Z preferences
           - Tailored trend insights for specific subgroups
        
        4. **AI-Driven Design Inspiration:** 
           - Transforming trends into visual prototypes with Stable Diffusion
           - Enabling rapid iteration and validation of designs
        """)

        st.subheader("Explore Our Tools")
        st.write("""
        Navigate through the sidebar to access our powerful features:
        - **Data Visualization:** Explore trend data visually
        - **Embedding Operations:** Analyze and manipulate fashion embeddings
        - **Clustering:** Discover trend patterns and groupings
        - **Prompt Generation:** Create AI-powered design inspirations
        """)

        st.info("Start your journey into the future of Gen Z fashion trend analysis!")
    elif page == 'Data Visualition':
        data_visualization()
            
    elif page == 'Embedding Operations':
        st.write("Perform Embedding Operations:")
        if st.button("Trigger Embedding Operations"):
            perform_embedding_operations()

    elif page == 'Clustering':
        st.write("Perform Clustering for GenZ Clothing Trends:")
        if st.session_state.combined_features is None:
            st.write("Loading combined features...")
            st.session_state.combined_features = load_combined_features('combined_features_4k_cleaned.pkl')
        st.write(f"Successfully loaded {len(st.session_state.combined_features)} product embeddings.")
        
        # Check if clustering results are cached
        if st.session_state.cached_clusters is None or st.session_state.cached_cluster_centers is None:
            # Add clustering parameters and perform clustering
            n_clusters = st.slider("Select number of clusters:", min_value=2, max_value=10, value=5, step=1)
            if st.button("Run Clustering"):
                preprocessed_features = preprocess_features(st.session_state.combined_features)
                st.session_state.cached_clusters, st.session_state.cached_cluster_centers = perform_clustering(preprocessed_features, n_clusters)
                st.write(f"Clustering completed with {n_clusters} clusters.")
                st.write(f"Cluster labels: {st.session_state.cached_clusters}")
        else:
            st.write("Using cached clustering results.")
            st.write(f"Cluster labels: {st.session_state.cached_clusters}")

        # Plotting the clusters
        if st.session_state.cached_clusters is not None and st.session_state.cached_cluster_centers is not None:
            fig, ax = plt.subplots()
            scatter = ax.scatter(st.session_state.combined_features[:, 0], st.session_state.combined_features[:, 1], c=st.session_state.cached_clusters, cmap='viridis', alpha=0.5)
            legend = ax.legend(*scatter.legend_elements(), title="Clusters")
            ax.add_artist(legend)
            st.pyplot(fig)

    elif page == 'Prompt Generation':
        st.write("Generate Prompt Based on Selected Cluster:")
        products = load_product_data("data.json")
        
        if st.session_state.cached_clusters is not None:
            selected_cluster = st.selectbox("Select a cluster:", sorted(set(st.session_state.cached_clusters)))

            products_in_cluster = [product for idx, product in enumerate(products) if st.session_state.cached_clusters[idx] == selected_cluster]

            if st.button("Generate Prompt"):
                combined_prompt = generate_combined_prompt(products_in_cluster)
                st.text_area("Generated Prompt", value=combined_prompt, height=200, max_chars=None, key=None)

                # Generate image based on the prompt
                try:
                    output_image, seed = generate_image(combined_prompt)
                    st.image(Image.open(io.BytesIO(output_image)), caption=f"Generated image (seed: {seed})")
                except Exception as e:
                    st.error(f"Error generating image: {str(e)}")
        else:
            st.write("Please run clustering on the 'Clustering' page first.")

if __name__ == "__main__":
    main()