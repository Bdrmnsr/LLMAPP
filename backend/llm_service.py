import os
from openai import OpenAI
import replicate
from database import query_vector_db  # Ensure this function is properly defined in your database.py
import time

# API keys are hardcoded for demonstration; consider using environment variables for production
OPENAI_API_KEY = "sk-proj-V9YbdWeV2gQVyaCZZvufT3BlbkFJhgXcASD8NrpF2y0o42Ro"
REPLICATE_API_KEY = "r8_SrGAOMo0OAytGgOey9KAVaqad4aTRlU2utolZ"

# API endpoints
llama_2_endpoint = "meta/llama-2-70b-chat"
falcon_40b_endpoint = "joehoover/falcon-40b-instruct:7d58d6bddc53c23fa451c403b2b5373b1e0fa094e4e0d1b98c3d02931aa07173"

# Set the environment variable for Replicate API token
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_KEY

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def query_openai_stream(user_prompt, search_results, model):
    """Query OpenAI using streaming with context provided from search results."""
    combined_prompt = f"{user_prompt}\n\nContext:\n" + "\n".join(search_results)
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            stream=True,
        )
        response = ""
        for chunk in stream:
            response += chunk.choices[0].delta.content or ""
        return response.strip()
    except Exception as e:
        return f"Error: {e}"

def query_replicate_llama(user_prompt, search_results):
    """Query the Replicate Llama model with context."""
    input = {
        "top_p": 1,
        "prompt": f"{user_prompt}\n\nContext:\n" + "\n".join(search_results),
        "temperature": 0.5,
        "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe."
    }
    try:
        output = replicate.run(llama_2_endpoint, input)
        return "".join(output)
    except Exception as e:
        return f"Error: {e}"

def query_replicate_falcon(user_prompt, search_results):
    """Query the Replicate Falcon model with context."""
    input = {
        "prompt": f"{user_prompt}\n\nContext:\n" + "\n".join(search_results),
        "temperature": 1
    }
    max_retries = 5
    attempts = 0
    while attempts < max_retries:
        try:
            output = replicate.run(falcon_40b_endpoint, input)
            if output:
                return "".join(output)
            else:
                time.sleep(5)  # Wait before retrying if the response is empty or pending
        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {str(e)}")
            if attempts >= max_retries - 1:
                return f"Error after {max_retries} attempts: {str(e)}"
            time.sleep(5)  # Wait before retrying if there's an error
        attempts += 1

    return "Failed to get a valid response from Falcon model."

def evaluate_responses(responses, user_prompt):
    """
    Evaluate responses based on relevance to the user prompt and the detailed content.
    """
    if isinstance(responses, tuple):
        responses = dict(responses)

    if not responses:
        return None, "No responses available"

    def score_response(response):
        # Simple keyword relevance score based on presence of query terms in response
        relevance = sum(1 for word in user_prompt.split() if word.lower() in response.lower())
        length_score = len(response)
        return relevance * 10 + length_score  # Weight relevance higher than length

    # Filter out any non-string or empty string responses to avoid processing errors
    valid_responses = {model: resp for model, resp in responses.items() if isinstance(resp, str) and resp.strip()}

    if not valid_responses:
        return None, "No valid responses available"

    # Score each response and find the one with the highest score
    best_model, best_response = max(valid_responses.items(), key=lambda x: score_response(x[1]))
    return best_model, best_response






def get_responses(user_prompt):
    """Retrieve the best response from all configured LLMs using the provided user prompt."""
    search_results = query_vector_db(user_prompt)
    responses = {
        "gpt-3.5-turbo": query_openai_stream(user_prompt, search_results, "gpt-3.5-turbo"),
        "gpt-4": query_openai_stream(user_prompt, search_results, "gpt-4"),
        "llama-2-70b-chat": query_replicate_llama(user_prompt, search_results),
        #"falcon-40b-instruct": query_replicate_falcon(user_prompt, search_results)
    }
    print(f"Type of responses: {type(responses)}")  # Check the type here
    best_model, best_response = evaluate_responses(responses, user_prompt)  # Pass user_prompt here
    return best_model, best_response



if __name__ == "__main__":
    user_prompt = "Explain the benefits of the golden visa in the UAE."
    best_model, best_response = get_responses(user_prompt)
    print(f"Best response from {best_model}: {best_response}")
