// src/NonauthApp.jsx

import React, { useState } from "react";
import "./App.css";
import InputWithoutAuth from "./components/InputFormWithoutAuth/InputFormWithoutAuth";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Recommendation } from "./components/Recommendation/Recommendation";
import Navbar from "./components/Navbar/Navbar";
import Footer from "./components/Footer/Footer";

function AppWithoutAuth() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (recommendationsData) => {
    setLoading(true);
    try {
      setRecommendations(recommendationsData);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="top-row">
        <div className="input-container">
          <InputWithoutAuth onSubmit={handleSubmit} />
        </div>
      </div>
      <div className="recommendations-container">
        {loading ? (
          <div className="loading-container">
            <div className="loader"></div>
            <p>Loading recommendations...</p>
          </div>
        ) : recommendations.length > 0 ? (
          <Recommendation recommendations={recommendations} />
        ) : null}
      </div>
      <Footer />
      <ToastContainer />
    </div>
  );
}

export default AppWithoutAuth;
