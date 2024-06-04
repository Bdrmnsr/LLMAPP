import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import pinecone
from sentence_transformers import SentenceTransformer
import logging

# Set your Pinecone API key
PINECONE_API_KEY = '4bd1fb3b-5bb0-42b5-a393-0c37ea6f3367'

# Initialize Pinecone with the new API
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to a Pinecone index
index_name = 'scraped-data'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Dimension of the embeddings
        metric='euclidean',
        spec=pinecone.ServerlessSpec(
            cloud='aws',
            region='us-east-1'  # Change to a supported region
        )
    )
index = pc.Index(index_name)

# Initialize Sentence Transformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url):
    """Fetch the content of the URL and handle potential network errors."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        return response.text
    except requests.exceptions.Timeout:
        logging.error(f"Timeout occurred when fetching {url}")
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error occurred when fetching {url}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error {e.response.status_code} on {url}")
    return None

def scrape_site(url, base_url, visited=set(), depth=0, max_depth=3):
    if url in visited or depth > max_depth:
        return
    visited.add(url)

    page_content = fetch_page(url)
    if page_content is None:
        return

    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        title_element = soup.find('title')
        title = title_element.text if title_element else "No title found"
        text_content = ' '.join(p.text for p in soup.find_all('p'))
        max_length = 20000  # Adjust based on expected text size
        truncated_content = text_content[:max_length]
        
        if text_content:
            embedding = model.encode(truncated_content).tolist()
            index.upsert([(url, embedding, {'title': title, 'content': truncated_content})])
            logging.info(f"Stored content from {url} in Pinecone")

        process_links(soup, url, base_url, visited, depth + 1, max_depth)
    except Exception as e:
        logging.error(f"An error occurred while processing {url}: {str(e)}")

def process_links(soup, current_url, base_url, visited, depth, max_depth):
    links = soup.find_all('a', href=True)
    filtered_links = set()
    for link in links:
        href = link['href']
        full_url = urllib.parse.urljoin(current_url, href)
        if full_url.startswith(base_url) and full_url not in visited:
            filtered_links.add(full_url)
    for link in filtered_links:
        time.sleep(1)  # Respectful delay between requests
        scrape_site(link, base_url, visited, depth + 1, max_depth)

def start_scraping(base_url, max_depth=3):
    visited_urls = set()
    scrape_site(base_url, base_url, visited_urls, max_depth=max_depth)

if __name__ == '__main__':
    main_url = 'https://u.ae/en/information-and-services'
    start_scraping(main_url)
