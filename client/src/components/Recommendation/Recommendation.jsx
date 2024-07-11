import React from "react";
import "./Recommendation.css";

export const Recommendation = ({ recommendations }) => {
  return (
    <div className="reco-container">
      <h2>Recommendations</h2>
      <ul>
        {recommendations.map((repo, index) => (
          <li key={index}>
            <div className="repo-card">
              <div className="repo-info">
                <h3>{repo.full_name}</h3>
                <p>{repo.description}</p>
                <div className="repo-details">
                  <span>Language: {repo.language}</span>
                  <span>Stars: {repo.stargazers_count}</span>
                  <span>Forks: {repo.forks_count}</span>
                  <span>Open Issues: {repo.open_issues_count}</span>
                  <span>Last Updated: {repo.updated_at}</span>
                </div>
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
              </div>
              <div className="repo-avatar">
                {repo.avatar_url && <img src={repo.avatar_url} alt="Avatar" />}
              </div>
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
          </li>
        ))}
      </ul>
    </div>
  );
};
