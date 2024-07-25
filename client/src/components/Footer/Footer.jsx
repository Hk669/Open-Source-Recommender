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
            <a
              href="https://github.com/Hk669"
              target="_blank"
              rel="noopener noreferrer"
            >
              Hrushikesh Dokala
            </a>
          </strong>
        </p>
        <p className="feedback">
          <a
            href="https://github.com/Hk669/Open-Source-Recommender/discussions/13"
            target="_blank"
            rel="noopener noreferrer"
          >
            Feedback
          </a>
        </p>
        <p className="feedback">
          <a
            href="https://github.com/Hk669/Open-Source-Recommender/discussions/1"
            target="_blank"
            rel="noopener noreferrer"
          >
            Tutorial
          </a>
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
