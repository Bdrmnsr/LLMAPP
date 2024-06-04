# Backend for LLM Evaluation Service

This backend service is designed to support the LLM Evaluation Web Application by handling data processing, model evaluations, and API requests.

## Description

The backend is built using Flask, a lightweight WSGI web application framework in Python. It is responsible for scraping data, managing a vector database, and interacting with different Large Language Models (LLMs) to evaluate responses based on user queries.

## Features

- **Web Scraping**: Automatically scrapes specified websites and stores the data for processing.
- **Vector Database Integration**: Manages a database to store and retrieve scraped data efficiently.
- **LLM Query Processing**: Handles requests to various LLMs like GPT-3.5-turbo, GPT-4, Llama-2-70b-chat, and Falcon-40b-instruct, and evaluates their responses.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software:

- Python 3.8+
- Flask
- Requests library for HTTP requests

### Installing

A step by step series of examples that tell you how to get a development environment running:

1. Clone the repository:
   ```bash
   git clone https://github.com/Bdrmnsr/LLMAPP.git
   cd LLMAPP/backend

# Install the required packages:
pip install -r requirements.txt

#Run the Flask application:
flask run

