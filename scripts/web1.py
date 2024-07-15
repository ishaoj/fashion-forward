import requests
from bs4 import BeautifulSoup

# Function to get HTML content from a URL
def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to parse HTML and extract data
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    print(soup)
    for title in soup.find_all('h2', class_='title'):
        titles.append(title.get_text())
    return titles

# Main function
def main():
    url = 'https://www.veromoda.in/'  # Replace with the URL you want to scrape
    html = get_html(url)
    if html:
        titles = parse_html(html)
        print("Article Titles:")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    else:
        print("Failed to retrieve the web page.")

if __name__ == "__main__":
    main()


