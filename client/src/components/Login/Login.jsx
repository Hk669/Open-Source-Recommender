// src/components/Login/Login.jsx
import React from "react";
import "./Login.css";
import { FaGithub } from "react-icons/fa";
import appImage from "../../assets/application.png";

const API_URL = process.env.REACT_APP_API_URL;

const API_URL = process.env.REACT_APP_API_URL;

const Login = () => {
  const handleLogin = () => {
    window.location.href = `${API_URL}/github-login`;
  };

  return (
    <div className="login-container">
      <h1>Search Your Next Open-Source Contribution with Ease!</h1>
      <p>
        Discover the perfect open-source projects to contribute to with this
        personalized recommendation system. Whether you're new to open source or
        a seasoned contributor, find relevant repositories tailored just for
        you.
      </p>
      <br></br>

      <button className="github-login-button" onClick={handleLogin}>
        <FaGithub className="github-icon" />
        <span>Connect Your GitHub</span>
      </button>

      <br></br>
      <div className="features-container">
        <div className="key-features">
          <h2>Key Features:</h2>
          <ul>
            <li>
              <strong>Personalized Recommendations:</strong> Get matched with
              the best open-source repositories based on your GitHub profile and
              current projects.
            </li>
            <li>
              <strong>Optional Preferences:</strong> Customize your
              recommendations by specifying preferred programming languages and
              additional topics.
            </li>
            <li>
              <strong>Ease of Use:</strong> Connect your GitHub account to get
              started and harness the power of the recommendation engine.
            </li>
            <li>
              <strong>Explore and Contribute:</strong> Expand your horizons by
              exploring new technologies and projects aligned with your
              interests and expertise.
            </li>
          </ul>
        </div>

        <div className="why-choose">
          <h2>Why Choose Open Source Recommender?</h2>
          <ul>
            <li>
              <strong>Relevancy:</strong> Ive seen goodfirstissues, but the
              problem is that they are not always relevant to my skills and
              interests.
            </li>
            <li>
              <strong>Efficiency:</strong> Save time finding projects that match
              your skills and interests.
            </li>
            <li>
              <strong>Exposure:</strong> Enables you to contribute to the
              open-source community and make a difference.
            </li>
            <li>
              <strong>Secure, Fast, and Free to Use:</strong> Access all
              features securely and quickly at no cost – a commitment to
              fostering open-source collaboration.
            </li>
          </ul>
        </div>
      </div>

      <br />

      <br></br>

      <div className="how-container">
        <div className="how">
          <h2>How It Works:</h2>
          <ul>
            <li>
              <strong>Connect Your GitHub Account:</strong>
              <br></br> Click the "Connect Your GitHub" button above to link
              your GitHub account.
            </li>
            <li>
              <strong>Customize Your Preferences:</strong>
              <br></br> Specify your preferred programming languages and
              additional topics to refine your recommendations.
            </li>
            <li>
              <strong>Get Recommendations:</strong>
              <br></br> Click "Get Recommendations" to receive a list of
              open-source repositories tailored to your profile and preferences.
            </li>
            <li>
              <strong>Explore and Contribute:</strong>
              <br></br> Browse through the recommended projects and start
              contributing to the open-source community.
            </li>
          </ul>
        </div>
        <div className="image-container">
          <img src={appImage} alt="Application"/>
        </div>
      </div>
    </div>
  );
};

export default Login;
