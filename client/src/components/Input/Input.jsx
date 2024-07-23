import React, { useState } from "react";
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
    setLanguageInput(e.target.value);
  };

  const handleExtraTopicInputChange = (e) => {
    setExtraTopicInput(e.target.value);
  };

  const handleLanguageInputKeyDown = (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addLanguage();
    }
  };

  const handleExtraTopicInputKeyDown = (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addExtraTopic();
    }
  };

  const addLanguage = () => {
    const trimmedInput = languageInput.trim();
    if (trimmedInput && !languages.includes(trimmedInput)) {
      setLanguages([...languages, trimmedInput]);
      setLanguageInput("");
    }
  };

  const addExtraTopic = () => {
    const trimmedInput = extraTopicInput.trim();
    if (trimmedInput && !extraTopics.includes(trimmedInput)) {
      setExtraTopics([...extraTopics, trimmedInput]);
      setExtraTopicInput("");
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
          onKeyDown={handleLanguageInputKeyDown}
          placeholder="Type and press Enter to add"
        />
      </label>
      <label>
        Extra Topics:
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
          onKeyDown={handleExtraTopicInputKeyDown}
          placeholder="Type and press Enter to add"
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
