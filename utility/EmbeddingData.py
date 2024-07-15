import streamlit as st
import torch
from transformers import BertModel, BertTokenizer
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import pickle
import json
import clip

# Prefix for image URLs
IMAGE_URL_PREFIX = "https://prod-img.thesouledstore.com/public/theSoul/uploads/catalog/product/"
device = "cuda" if torch.cuda.is_available() else "cpu"
image_model, preprocess = clip.load("ViT-B/32", device=device)

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to load and preprocess product data from a JSON file
json_file = 'souled_store_products.json'

def load_product_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

def get_image_urls(product):
    return [IMAGE_URL_PREFIX + img for img in product['images']]

def extract_text_features(products):
    descriptions = [prod.get('short_desc', '') for prod in products]
    inputs = tokenizer(descriptions, return_tensors='pt', truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Extract embeddings
    embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
    
    return embeddings

def extract_image_features(image_urls):
    features = []
    for url in image_urls:
        response = requests.get(url)

        img = Image.open(BytesIO(response.content)).convert("RGB")
        # st.image(img, caption="Image for Embedding", use_column_width=True)

        img_preprocessed = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            feature = image_model.encode_image(img_preprocessed)
        features.append(feature.cpu().numpy().flatten())
    return np.mean(features, axis=0)  

def combine_features(image_features, text_features):
    combined_features = []
    for img_feat, txt_feat in zip(image_features, text_features):
        combined = np.concatenate((img_feat, txt_feat), axis=None)
        combined_features.append(combined)
    return np.array(combined_features)

def perform_embedding_operations():
    st.write("Performing Embedding Operations...")

    # Load products
    products = load_product_data(json_file)

    # Initialize CLIP model if not already initialized
    global image_model, preprocess
    if image_model is None:
        image_model, preprocess = None, None  # Initialize CLIP model here

    # Extract features
    image_features = []
    
    text_features = extract_text_features(products)

    # Use st.progress to simulate progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, product in enumerate(products):
        st.subheader(product['breadcrum_name'])
        image_urls = get_image_urls(product)
        img_features = extract_image_features(image_urls)
        image_features.append(img_features)

        # Display product name and images being processed
        
        # st.image(image_urls, caption="Images for Embedding", width=200)

        # Update progress bar and status text
        progress_bar.progress((idx + 1) / len(products))
        status_text.text(f"Processing product {idx + 1}/{len(products)}")
        st.empty()

    combined_features = combine_features(image_features, text_features)

    # Save combined features to file
    with open('combined_features.pkl', 'wb') as f:
        pickle.dump(combined_features, f)

    # Update status text when done
    status_text.text("Embedding Operations Completed!")


