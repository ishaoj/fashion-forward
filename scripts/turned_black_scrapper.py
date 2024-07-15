import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
def get_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        sitemap_content = response.content
        root = ET.fromstring(sitemap_content)
        
        urls = []
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(url.text)
        
        return urls
    else:
        print(f"Failed to retrieve sitemap: {response.status_code}")
        return []

# Replace with the URL of your sitemap
sitemap_url = 'https://www.turnblack.in/product-sitemap.xml'
urls = get_urls_from_sitemap(sitemap_url)
product_list = []
store_data = []
for url in urls:
    product_list.append(url)
    print(url)
product_list = product_list[1:]
for url in tqdm(product_list):
    try:

        # Send a GET request to the URL
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize a dictionary to hold the scraped data
            data = {
                "title": "",
                "images": [],
                "product_description": "",
                "price": "",
                "sku": "",
                "categories": []
            }
            
            # Find the element with class name "product_title entry-title"
            product_title = soup.find(class_="product_title entry-title")
            if product_title:
                data["title"] = product_title.get_text(strip=True)
            else:
                data["title"] = "Product title not found."
            
            # Find all elements with class name "wp-post-image"
            images = soup.find_all(class_="wp-post-image")
            for img in images:
                img_url = img['src']  # Assuming the image URL is in the 'src' attribute
                data["images"].append(img_url)
            
            # Find the element with class name "woocommerce-product-details__short-description"
            product_description = soup.find(class_="woocommerce-product-details__short-description")
            if product_description:
                description_text = product_description.get_text(strip=True)
                data["product_description"] = description_text
            else:
                data["product_description"] = "Product description not found."
            
            # Find the element with class name "woocommerce-Price-amount amount"
            product_price = soup.find(class_="woocommerce-Price-amount amount")
            if product_price:
                data["price"] = product_price.get_text(strip=True)
            else:
                data["price"] = "Price not found."
            
            # Find the SKU and categories in the product meta
            product_meta = soup.find(class_="product_meta")
            
            # Find the SKU
            sku = product_meta.find(class_="sku")
            if sku:
                data["sku"] = sku.get_text(strip=True)
            else:
                data["sku"] = "SKU not found."
            
            # Find the categories
            categories = product_meta.find(class_="posted_in")
            if categories:
                category_links = categories.find_all("a")
                data["categories"] = [category.get_text(strip=True) for category in category_links]
            else:
                data["categories"] = ["Categories not found."]
            
            # Write the data to a JSON file

            store_data.append(data)
            print("Data successfully scraped and stored in scraped_data.json")
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
    except:
        print("Failed")
with open('scraped_data.json', 'w') as json_file:
    json.dump(store_data, json_file, indent=4)