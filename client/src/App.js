import React, { useState } from "react";
import "./App.css";
import Input from "./components/Input/Input";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Recommendation } from "./components/Recommendation/Recommendation";
import { Navbar } from "./components/Navbar/Navbar";

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (recommendations) => {
    setLoading(true);
    console.log("recommendations");
    console.log(recommendations);

    setRecommendations(recommendations);
    setLoading(false);
  };

  return (
    <div className="App">
      <Navbar />
      <div className="App-main">
        <div className="Input">
          <Input onSubmit={handleSubmit} />
        </div>
        {loading ? (
          <p>Loading recommendations...</p>
        ) : recommendations.length > 0 ? (
          <div className="Recommendation">
            <Recommendation recommendations={recommendations} />
          </div>
        )
          : null}
        <ToastContainer />
      </div>
    </div>
  );
}

export default App;
