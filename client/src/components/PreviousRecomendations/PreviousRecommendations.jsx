import React, { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";

const PreviousRecommendations = ({ userData }) => {
  const [recommendationIds, setRecommendationIds] = useState([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendationIds = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/user-recommendations?username=${encodeURIComponent(
            userData.username
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response.ok) {
          const data = await response.json();

          if (Array.isArray(data)) {
            setRecommendationIds(data.map((rec) => rec.recommendation_id));
          } else {
            throw new Error("Invalid data format: Expected an array");
          }
        } else {
          throw new Error("Failed to fetch previous recommendations");
        }
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendationIds();
  }, [userData.username]);

  const fetchRecommendationDetails = async (recommendationId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/recommendation/${recommendationId}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setSelectedRecommendation(data.recommendations || []);
      } else {
        throw new Error("Failed to fetch recommendation details");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const timeAgo = (date) =>
    formatDistanceToNow(new Date(date), { addSuffix: true });

  return (
    <div className="reco-container">
      <h2>Previous Recommendations</h2>
      {loading && <p>Loading...</p>}
      {error && <p className="error-message">Error: {error}</p>}
      <ul className="recommendation-ids">
        {recommendationIds.map((id, index) => (
          <li key={index}>
            <button onClick={() => fetchRecommendationDetails(id)}>{id}</button>
          </li>
        ))}
      </ul>

      {selectedRecommendation && (
        <div className="selected-recommendation">
          <h2>Recommendation Details</h2>
          <ul className="repo-ul">
            {selectedRecommendation.map((repo, index) => (
              <li key={index}>
                <div className="repo-card">
                  <div className="repo-info">
                    <a href={repo.repo_url}>
                      <h3>{repo.full_name}</h3>
                    </a>
                    <p>{repo.description}</p>
                    <div className="topics-container">
                      <span>Topics: </span>
                      {repo.topics
                        .split(", ")
                        .slice(0, 7)
                        .map((topic, idx) => (
                          <div key={idx} className="topic">
                            {topic}
                          </div>
                        ))}
                    </div>
                    <br />
                    <div className="repo-details">
                      <span>
                        ⭐ {Math.round(repo.stargazers_count / 100) / 10}k
                      </span>
                      <span>🔵 {repo.language}</span>
                      <span>issues: {repo.open_issues_count}</span>
                      <span>forks: {repo.forks_count}</span>
                      <span>Updated {timeAgo(repo.updated_at)}</span>
                    </div>
                    <br />
                    <div className="repo-link">
                      <a
                        href={repo.repo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View Repository
                      </a>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PreviousRecommendations;
