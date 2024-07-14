import React from "react";
import "./Recommendation.css";
import { formatDistanceToNow } from "date-fns";
import { useEffect, useRef } from "react";

export const Recommendation = ({ recommendations }) => {
  const recoRef = useRef(null);

  useEffect(() => {
    if (recommendations.length > 0 && recoRef.current) {
      recoRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [recommendations]);


  const timeAgo = (date) =>
    formatDistanceToNow(new Date(date), { addSuffix: true });

  return (
    <div className="reco-container" ref={recoRef}>
      <h2>Recommendations</h2>
      <ul className="repo-ul">
        {recommendations.map((repo, index) => (
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
                <br></br>
                <div className="repo-details">
                  <span>
                    ⭐ {Math.round(repo.stargazers_count / 100) / 10}k
                  </span>
                  <span>🔵 {repo.language}</span>
                  <span>issues: {repo.open_issues_count}</span>
                  <span>forks: {repo.forks_count}</span>
                  <span>Updated {timeAgo(repo.updated_at)}</span>
                </div>
                <br></br>
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
  );
};
