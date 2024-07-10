// utils/auth.js
import axios from "axios";

export const refreshToken = async () => {
  try {
    const currentToken = localStorage.getItem("session_token");
    const response = await axios.post(
      "http://127.0.0.1:8000/refresh-token",
      {},
      {
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      }
    );
    const newToken = response.data.session_token;
    localStorage.setItem("session_token", newToken);
    return newToken;
  } catch (error) {
    console.error("Error refreshing token:", error);
    localStorage.removeItem("session_token");
    window.location.href = "/login";
  }
};
