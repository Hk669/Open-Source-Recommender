// src/utils/auth.js
import axios from "axios";

export const refreshToken = async () => {
  const currentToken = localStorage.getItem("jwt_token");
  try {
    const response = await axios.post(
      `${process.env.REACT_APP_API_URL}/refresh-token`,
      {},
      {
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      }
    );
    const newToken = response.data.jwt;
    localStorage.setItem("jwt_token", newToken);
    return newToken;
  } catch (error) {
    console.error("Error refreshing token:", error);
    localStorage.removeItem("jwt_token");
    window.location.href = "/login";
  }
};
