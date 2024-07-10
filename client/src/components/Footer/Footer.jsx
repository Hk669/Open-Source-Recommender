import React from "react";
import { FaGithub, FaLinkedin, FaTwitter } from "react-icons/fa";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>
          Developed by{" "}
          <strong>
            <a href="https://github.com/Hk669">Hrushikesh Dokala</a>
          </strong>
        </p>
        <div className="social-links">
          <a
            href="https://github.com/Hk669/Open-Source-Recommender"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaGithub />
          </a>
          <a
            href="https://linkedin.com/in/hrushikeshdokala"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaLinkedin />
          </a>
          <a
            href="https://twitter.com/hrushikeshhhh"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaTwitter />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
