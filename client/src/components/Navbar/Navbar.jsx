import React from "react";
import logo from "../../assets/logo.png";
import "./Navbar.css"; // We'll create this file for styling
import { Link } from "react-router-dom";

function Navbar({ isAuthenticated, userData, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="logo">
          <Link to="/">
            <img src={logo} alt="logo" />
          </Link>
        </div>
        <div className="nav-items">
          {isAuthenticated ? (
            <>
              <button className="logout-button" onClick={onLogout}>
                Logout
              </button>
            </>
          ) : (
            <></>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
