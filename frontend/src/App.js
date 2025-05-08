import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import backgroundImage from './fd08b1c9cc81d4d267adf6799fbf08f3.gif'; // Import your GIF

function App() {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('');

  const handleSubmit = async () => {
    try {
      const res = await axios.post('https://knowledge-representation-graph.onrender.com/generate-graph', { text });
      setImage(`data:image/png;base64,${res.data.image}`);
      setConnectionStatus('Graph generated successfully!');
    } catch (error) {
      console.error("Error sending request to generate graph:", error);
      console.error("Full error object:", error);
      setImage(null);
      setConnectionStatus('Error generating graph. Check backend connection.');
    }
  };

  const testBackend = async () => {
    try {
      const response = await axios.get('https://knowledge-representation-graph.onrender.com/test-connection');
      console.log("Backend response:", response.data);
      setConnectionStatus(response.data.message);
    } catch (error) {
      console.error("Error testing backend connection:", error);
      setConnectionStatus('Failed to connect to backend.');
    }
  };

  return (
    <div className="app-container" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <h1 className="app-title">Knowledge Representation Graph Generator</h1>
      <textarea
        rows={8}
        cols={90}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text here..."
        className="input-textarea"
      />
      <br />
      <div className="button-container">
        <button onClick={handleSubmit} className="generate-button">
          Generate Graph
        </button>
        {/* <button onClick={testBackend} className="test-button">
          Test Backend Connection
        </button> */}
      </div>
      {connectionStatus && <p className="status-message">Status: {connectionStatus}</p>}
      {image && (
        <div className="graph-container">
          <h2 className="graph-title">Generated Graph:</h2>
          <img src={image} alt="Knowledge Graph" className="graph-image" />
        </div>
      )}
    </div>
  );
}

export default App;