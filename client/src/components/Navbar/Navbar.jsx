import React from "react";
import "./Navbar.css"; // Import CSS file for styling

export const Navbar = () => {
  return (
    <div className="navbar">
      <div className="logo">Logo</div>
      <ul className="nav-links">
        <li>
          <a href="#">
            <img
              src="https://img.icons8.com/?size=50&id=59809&format=png&color=000000"
              alt="home"
            />
          </a>
        </li>
        <li>
          <a href="https://github.com/Hk669">
            <img
              src="https://img.icons8.com/?size=50&id=62856&format=png&color=000000"
              alt="github"
            />
          </a>
        </li>
      </ul>
    </div>
  );
};

