import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);  // State to track loading status

  const handlePromptSubmit = async (event) => {
    event.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a valid prompt.');
      setResponse('');
      return;
    }

    setError('');
    setResponse('');
    setIsLoading(true); // Set loading to true when the request starts

    try {
      const res = await axios.post('http://localhost:5000/query-llm', { prompt });
      if (res.data.error) {
        setError(res.data.error);
      } else {
        setResponse(`Best Model: ${res.data.best_model}\nResponse: ${res.data.best_response}`);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to fetch response');
    }

    setIsLoading(false); // Set loading to false when the request completes
  };

  return (
    <div className="App">
      <h1>The UAE Government Portal Website Q&A</h1>
      <form onSubmit={handlePromptSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Ask'}
        </button>
      </form>
      {response && <pre>{response}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;
