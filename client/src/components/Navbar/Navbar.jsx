import React from "react";
import logo from "../../assets/logo.png";
import "./Navbar.css"; // We'll create this file for styling

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="logo">
          <a href="/">
            <img src={logo} alt="logo" />
          </a>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
