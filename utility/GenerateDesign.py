import random
from collections import Counter

def extract_product_info(product_data):
    """Extracts relevant information from a product data dictionary."""
    product_type = product_data.get('category', 'T-Shirt')
    style = product_data.get('fittype', 'Regular Fit')  # Using fittype for style
    colors = [color['color_name'] for color in product_data.get('colors', [])]
    material = product_data.get('fabric_name', 'Cotton')
    design_themes = [tag['tag_name'] for tag in product_data.get('tags', [])]
    return product_type, style, colors, material, design_themes

def generate_combined_prompt(product_data_list):
    """Generates a combined prompt from a list of product data.

    Args:
    - product_data_list: A list of dictionaries containing product information.
    - num_products: Number of products to select from the list.

    Returns:
    A string representing the combined prompt.
    """
    # Extract all attributes from product_data_list
    all_product_types, all_styles, all_colors, all_materials, all_design_themes = [], [], [], [], []
    for product_data in product_data_list:
        product_type, style, colors, material, design_themes = extract_product_info(product_data)
        all_product_types.append(product_type)
        all_styles.append(style)
        all_colors.extend(colors)
        all_materials.append(material)
        all_design_themes.extend(design_themes)

    # Count occurrences of each attribute
    product_type_counts = Counter(all_product_types)
    style_counts = Counter(all_styles)
    color_counts = Counter(all_colors)
    material_counts = Counter(all_materials)
    design_theme_counts = Counter(all_design_themes)

    # Select top values for each attribute
    top_product_types = [key for key, _ in product_type_counts.most_common(3)]
    top_styles = [key for key, _ in style_counts.most_common(3)]
    top_colors = [key for key, _ in color_counts.most_common(10)]
    top_materials = [key for key, _ in material_counts.most_common(3)]
    top_design_themes = [key for key, _ in design_theme_counts.most_common(10)]

    # Randomly select values from top lists
    selected_product_type = random.choice(top_product_types)
    selected_style = random.choice(top_styles)
    selected_colors = random.sample(top_colors, min(3, len(top_colors)))
    selected_material = random.choice(top_materials)
    selected_design_themes = random.sample(top_design_themes, min(3, len(top_design_themes)))

    # Combine information into a prompt
    prompt = f"Design a trendy, {selected_style}-fit {selected_product_type} for Gen Z. "
    prompt += f"Use a combination or any one of {selected_material} materials with a diverse color palette including {', '.join(selected_colors)}. "
    prompt += f"Incorporate design elements inspired by {', '.join(selected_design_themes)}. "
    prompt += "Aim for a versatile and visually striking design that appeals to a wide Gen Z audience."
    prompt += " Generate a realistic, photorealistic image of the clothe or fashion item."

    return prompt
