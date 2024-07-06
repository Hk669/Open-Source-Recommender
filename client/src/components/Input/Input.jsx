import React, { useState } from "react";
import axios from "axios";
import "./Input.css";
import { toast } from "react-toastify";


const Input = ({ onSubmit }) => {
  const [username, setUsername] = useState("");
  const [languages, setLanguages] = useState("");
  const [extraTopics, setExtraTopics] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/recommendations/",
        {
          username,
          languages: languages.split(",").map((item) => item.trim()),
          extra_topics: extraTopics.split(",").map((item) => item.trim()),
        }
      );
      console.log(languages)
      console.log(extraTopics)
      onSubmit(response.data.recommendations);
    } catch (error) {
      if (error.response) {
        // Errors from the server
        toast.error(`${error.response.data.detail}`, {
          position: "top-right",
        });
      } else if (error.request) {
        // Network errors
        toast.error("Network error. Please try again later.", {
          position: "top-right",
        });
      } else {
        // Other errors
        toast.error(`An unexpected error occurred: ${error.message}`, {
          position: "top-right",
        });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        GitHub Username:
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </label>
      <label>
        Preferred Languages (comma separated):
        <input
          type="text"
          value={languages}
          onChange={(e) => setLanguages(e.target.value)}
        />
      </label>
      <label>
        Extra Topics (comma separated):
        <input
          type="text"
          value={extraTopics}
          onChange={(e) => setExtraTopics(e.target.value)}
        />
      </label>
      <button type="submit">Get Recommendations</button>
    </form>
  );
};

export default Input;
