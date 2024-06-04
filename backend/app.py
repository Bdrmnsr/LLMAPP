from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from scraper import start_scraping
from database import query_vector_db, initialize_index, delete_index
from llm_service import get_responses, evaluate_responses

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

# Setup basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return "Welcome to the LLM Evaluation Service!"

@app.route('/start-scraping', methods=['POST'])
def start_scraping_route():
    """Endpoint to start the web scraping process."""
    data = request.get_json()
    url = data.get('url', 'https://u.ae/en/information-and-services')
    max_depth = data.get('max_depth', 3)
    try:
        start_scraping(url, max_depth)
        return jsonify({"message": "Scraping started successfully", "url": url, "max_depth": max_depth}), 200
    except Exception as e:
        logging.error(f"Failed to start scraping: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/query-llm', methods=['POST'])
def query_llm():
    data = request.get_json()
    user_prompt = data.get('prompt')
    if not user_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Directly get the best model and response from the get_responses function
    best_model, best_response = get_responses(user_prompt)

    if best_model is None:
        return jsonify({"error": "Failed to evaluate responses or no valid responses"}), 500

    return jsonify({"best_model": best_model, "best_response": best_response}), 200



@app.route('/initialize-index', methods=['GET'])
def initialize_index_route():
    """Endpoint to initialize or reset the Pinecone index."""
    initialize_index()
    return jsonify({"message": "Index initialized or reset successfully"}), 200

@app.route('/delete-index', methods=['DELETE'])
def delete_index_route():
    """Endpoint to delete the Pinecone index."""
    delete_index()
    return jsonify({"message": "Index deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
