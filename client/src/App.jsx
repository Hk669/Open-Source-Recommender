import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import Input from "./components/Input/Input";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Recommendation } from "./components/Recommendation/Recommendation";
import Navbar from "./components/Navbar/Navbar";
import Footer from "./components/Footer/Footer";
import Login from "./components/Login/Login";
import { useNavigate, useLocation } from "react-router-dom";
import { Routes, Route } from "react-router-dom";
import GithubCallback from "./components/GithubCallback";
import PreviousRecommendations from "./components/PreviousRecommendations/PreviousRecommendations";

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const [showInput, setShowInput] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("jwt_token");
      if (token) {
        try {
          const response = await fetch(
            `${process.env.REACT_APP_API_URL}/verify-token`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            }
          );
          if (response.ok) {
            const data = await response.json();
            setIsAuthenticated(true);
            setUserData(data);
            if (location.pathname === "/") navigate("/recommender");
          } else {
            localStorage.removeItem("jwt_token");
            navigate("/");
          }
        } catch (error) {
          console.error("Error verifying token:", error);
          navigate("/");
        }
      }
    };

    checkAuth();
  }, [navigate, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    setIsAuthenticated(false);
    setUserData(null);
    navigate("/");
  };

  const handleSubmit = async (inputData) => {
    setLoading(true);
    try {
      setRecommendations(inputData);
      navigate("/recommender");
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousRecommendationSelect = useCallback(
    (selectedRecommendation, recommendationId) => {
      setRecommendations(selectedRecommendation);
      setShowInput(false);
      navigate(`/recommender/${recommendationId}`);
    },
    [navigate]
  );

  useEffect(() => {
    if (location.pathname === "/recommender") {
      setShowInput(true);
    }
  }, [location]);

  return (
    <div className="App">
      <Navbar
        isAuthenticated={isAuthenticated}
        userData={userData}
        onLogout={handleLogout}
      />
      <div className="app-container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/auth-callback" element={<GithubCallback />} />
          <Route
            path="/recommender"
            element={
              isAuthenticated ? (
                <>
                  <div className="top-row">
                    {showInput && (
                      <div className="input-container">
                        <Input onSubmit={handleSubmit} userData={userData} />
                      </div>
                    )}
                    <div className="previous-recommendations-container">
                      <PreviousRecommendations
                        userData={userData}
                        onSelectPreviousRecommendation={
                          handlePreviousRecommendationSelect
                        }
                      />
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
                </>
              ) : (
                <Login />
              )
            }
          />
          <Route
            path="/recommender/:id"
            element={
              isAuthenticated ? (
                <>
                  <div className="top-row">
                    <div className="previous-recommendations-container">
                      <PreviousRecommendations
                        userData={userData}
                        onSelectPreviousRecommendation={
                          handlePreviousRecommendationSelect
                        }
                      />
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
                </>
              ) : (
                <Login />
              )
            }
          />
          <Route path="*" element={<Login />} />
        </Routes>
      </div>
      <ToastContainer />
      <Footer />
    </div>
  );
}

export default App;
