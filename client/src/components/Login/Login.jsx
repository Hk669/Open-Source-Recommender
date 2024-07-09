// src/components/Login/Login.jsx
import React from "react";
import "./Login.css";
import { FaGithub } from "react-icons/fa";

const Login = () => {
  const handleLogin = () => {
    window.location.href = "http://127.0.0.1:8000/github-login";
  };

  return (
    <div className="login-container">
      <h2>Welcome Back</h2>
      <button className="github-login-button" onClick={handleLogin}>
        <FaGithub className="github-icon" />
        <span>Connect Your GitHub</span>
      </button>
    </div>
  );
};

export default Login;
