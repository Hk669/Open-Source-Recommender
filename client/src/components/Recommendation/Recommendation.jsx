import React from "react";
import "./Recommendation.css";

export const Recommendation = ({ recommendations }) => {
  return (
    <div className="reco-container">
      <ul>
        {recommendations.map((url, index) => (
          <li key={index}>
            <a href={url} target="_blank" rel="noopener noreferrer">
              {url}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};
