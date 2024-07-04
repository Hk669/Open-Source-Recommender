import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [languages, setLanguages] = useState("");
  const [extraTopics, setExtraTopics] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("/api/recommendations/", {
        username: username,
        languages: languages.split(",").map((lang) => lang.trim()),
        extra_topics: extraTopics.split(",").map((topic) => topic.trim()),
      });
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error("There was an error fetching recommendations:", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Repository Recommendations</h1>
      </header>
      <form onSubmit={handleSubmit}>
        <label>
          GitHub Username:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>
        <br />
        <label>
          Languages (comma-separated):
          <input
            type="text"
            value={languages}
            onChange={(e) => setLanguages(e.target.value)}
          />
        </label>
        <br />
        <label>
          Extra Topics (comma-separated):
          <input
            type="text"
            value={extraTopics}
            onChange={(e) => setExtraTopics(e.target.value)}
          />
        </label>
        <br />
        <button type="submit">Get Recommendations</button>
      </form>
      <div>
        <h2>Recommendations:</h2>
        <ul>
          {recommendations.map((url, index) => (
            <li key={index}>
              <a href={url}>{url}</a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
