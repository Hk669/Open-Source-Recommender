import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const GithubCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authenticated = urlParams.get("authenticated");
    const jwtToken = urlParams.get("jwt");

    if (authenticated === "true" && jwtToken) {
      localStorage.setItem("jwt_token", jwtToken);
      navigate("/recommender");
    } else {
      navigate("/");
    }
  }, [navigate]);

  return <div>Loading...</div>;
};

export default GithubCallback;
