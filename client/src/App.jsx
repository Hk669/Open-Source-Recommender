import React, { useState, useEffect } from "react";
import "./App.css";
import Input from "./components/Input/Input";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Recommendation } from "./components/Recommendation/Recommendation";
import Navbar from "./components/Navbar/Navbar";
import Footer from "./components/Footer/Footer";
import Login from "./components/Login/Login";
import { useNavigate } from "react-router-dom";
import { Routes, Route } from "react-router-dom";
import GithubCallback from "./components/GithubCallback";
import PreviousRecommendations from "./components/PreviousRecomendations/PreviousRecommendations";

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

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
            navigate("/recommender");
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
  }, [navigate]);

  const handleSubmit = async (inputData) => {
    setLoading(true);
    try {
      setRecommendations(inputData);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    setIsAuthenticated(false);
    setUserData(null);
    navigate("/login");
  };

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
                  <div
                    className={`form-container ${
                      recommendations.length > 0 ? "with-recommendations" : ""
                    }`}
                  >
                    <Input onSubmit={handleSubmit} userData={userData} />
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
                  <PreviousRecommendations userData={userData} />
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