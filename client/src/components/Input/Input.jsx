import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Input.css";
import { toast } from "react-toastify";

const Input = ({ onSubmit }) => {
  const [username, setUsername] = useState("");
  const [languages, setLanguages] = useState([]);
  const [extraTopics, setExtraTopics] = useState([]);
  const [languageInput, setLanguageInput] = useState("");
  const [extraTopicInput, setExtraTopicInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const jwtToken = localStorage.getItem("jwt_token");
    if (!jwtToken) {
      toast.error("JWT token not found. Please log in.", {
        position: "top-right",
      });
      return;
    }

    if (!username) {
      toast.error("GitHub username is required.", {
        position: "top-right",
      });
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/api/recommendations/`,
        {
          username: username,
          languages: languages,
          extra_topics: extraTopics,
        },
        {
          headers: {
            Authorization: `Bearer ${jwtToken}`,
          },
        }
      );

      if (
        response.data.success === false &&
        response.data.message === "Reached your daily limit"
      ) {
        toast.info(
          "You have reached your daily limit. Please try again tomorrow.",
          {
            position: "top-right",
          }
        );
      } else {
        onSubmit(response.data.recommendations);
      }
    } catch (error) {
      if (error.response) {
        toast.error(`${error.response.data.detail}`, {
          position: "top-right",
        });
      } else if (error.request) {
        toast.error("Network error. Please try again later.", {
          position: "top-right",
        });
      } else {
        toast.error(`An unexpected error occurred: ${error.message}`, {
          position: "top-right",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageInputChange = (e) => {
    const value = e.target.value;
    setLanguageInput(value);

    // Check for comma and update state
    if (value.includes(",")) {
      const newLanguages = value
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item && !languages.includes(item));
      if (newLanguages.length > 0) {
        setLanguages([...languages, ...newLanguages]);
      }
      setLanguageInput(""); // Clear input field after adding
    }
  };

  const handleExtraTopicInputChange = (e) => {
    const value = e.target.value;
    setExtraTopicInput(value);

    // Check for comma and update state
    if (value.includes(",")) {
      const newTopics = value
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item && !extraTopics.includes(item));
      if (newTopics.length > 0) {
        setExtraTopics([...extraTopics, ...newTopics]);
      }
      setExtraTopicInput(""); // Clear input field after adding
    }
  };

  const removeLanguage = (language) => {
    setLanguages(languages.filter((lang) => lang !== language));
  };

  const removeExtraTopic = (topic) => {
    setExtraTopics(extraTopics.filter((t) => t !== topic));
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        GitHub Username:
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled
        />
      </label>
      <label>
        Preferred Languages:
        <div className="tag-container">
          {languages.map((lang, index) => (
            <span key={index} className="tag">
              {lang}
              <button type="button" onClick={() => removeLanguage(lang)}>
                &times;
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          value={languageInput}
          onChange={handleLanguageInputChange}
          placeholder="Type languages separated by commas"
        />
      </label>
      <label>
        Preferred Topics:
        <div className="tag-container">
          {extraTopics.map((topic, index) => (
            <span key={index} className="tag">
              {topic}
              <button type="button" onClick={() => removeExtraTopic(topic)}>
                &times;
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          value={extraTopicInput}
          onChange={handleExtraTopicInputChange}
          placeholder="Type topics separated by commas"
        />
      </label>
      <button type="submit" disabled={loading}>
        {loading ? "Fetching Recommendations..." : "Get Recommendations"}
      </button>
      <p>*Open Source Recommender can make mistakes</p>
    </form>
  );
};

export default Input;
