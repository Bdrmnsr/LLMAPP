import os
import pinecone
from sentence_transformers import SentenceTransformer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Pinecone API key
PINECONE_API_KEY = '4bd1fb3b-5bb0-42b5-a393-0c37ea6f3367'

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Index specifications
index_name = 'scraped-data'
dimension = 768
metric = 'cosine'
cloud = 'aws'
region = 'us-east-1'

def initialize_index():
    """Initialize or reset the Pinecone index."""
    # Get the current list of indexes and log it to see the structure
    existing_indexes_response = pc.list_indexes()
    logging.info(f"Existing indexes: {existing_indexes_response}")
    
    # Assuming the response is a list directly or a dictionary containing a list under 'indexes'
    existing_indexes = [index['name'] for index in existing_indexes_response.get('indexes', [])]

    # Check if the index already exists
    if index_name in existing_indexes:
        logging.info(f"Index '{index_name}' already exists.")
    else:
        # If the index does not exist, create it
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=pinecone.ServerlessSpec(cloud=cloud, region=region)
        )
        logging.info(f"New index '{index_name}' created.")



# Ensure the index is initialized on module import
initialize_index()

# Create index instance
index = pc.Index(index_name)

# Initialize the Sentence Transformer model
model = SentenceTransformer('all-mpnet-base-v2')

def insert_data(url, text_content):
    """Insert text content into the Pinecone index."""
    try:
        embedding = model.encode(text_content).tolist()
        index.upsert([(url, embedding)])
        logging.info(f"Inserted data for URL: {url}")
    except Exception as e:
        logging.error(f"Error inserting data into Pinecone for URL {url}: {str(e)}")

def query_vector_db(query_text, top_k=5):
    """Query the Pinecone index to find the most relevant documents based on the query text."""
    try:
        query_vector = model.encode(query_text).tolist()
        # Correcting the query call as per the latest Pinecone SDK updates
        results = index.query(vector=query_vector, top_k=top_k)
        # Assuming results are being accessed correctly
        return [match['id'] for match in results['matches']]
    except Exception as e:
        logging.error(f"Error querying Pinecone database: {str(e)}")
        return []



def delete_index():
    """Delete the Pinecone index."""
    try:
        if index_name in pc.list_indexes():
            pc.delete_index(index_name)
            logging.info("Deleted Pinecone index successfully.")
    except Exception as e:
        logging.error(f"Error deleting Pinecone index: {str(e)}")
