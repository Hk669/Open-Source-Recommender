import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import App from "./App";
import GithubCallback from "./components/GithubCallback";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <Router>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/auth-callback" element={<GithubCallback />} />
      <Route path="/recommender" element={<App />} />
    </Routes>
  </Router>
);
