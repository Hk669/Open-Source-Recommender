import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const GithubCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authenticated = urlParams.get("authenticated");
    const accessToken = urlParams.get("access_token");

    if (authenticated === "true" && accessToken) {
      localStorage.setItem("github_token", accessToken);
      navigate("/recommender");
    } else {
      navigate("/");
    }
  }, [navigate]);

  return <div>Loading...</div>;
};

export default GithubCallback;
