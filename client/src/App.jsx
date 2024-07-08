import React, { useState } from "react";
import "./App.css";
import Input from "./components/Input/Input";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Recommendation } from "./components/Recommendation/Recommendation";
import Navbar from "./components/Navbar/Navbar";
import Footer from "./components/Footer/Footer";

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (inputData) => {
    setLoading(true);
    try {
      setRecommendations(inputData);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      // You might want to show an error message to the user here
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Navbar />
      <div className="app-container">
        <div
          className={`form-container ${
            recommendations.length > 0 ? "with-recommendations" : ""
          }`}
        >
          <Input onSubmit={handleSubmit} />
        </div>
        <div
          className={`recommendations-container ${
            recommendations.length > 0 ? "visible" : ""
          }`}
        >
          {loading ? (
            <div className="loading-container">
              <div className="loader"></div>
              <p>Loading recommendations...</p>
            </div>
          ) : recommendations.length > 0 ? (
            <Recommendation recommendations={recommendations} />
          ) : null}
        </div>
      </div>
      <ToastContainer />
      <Footer />
    </div>
  );
}

export default App;
