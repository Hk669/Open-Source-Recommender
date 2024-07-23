import React, {
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
} from "react";
import { formatDistanceToNow } from "date-fns";
import { useParams, useNavigate } from "react-router-dom";

const PreviousRecommendations = React.memo(
  ({ userData, onSelectPreviousRecommendation }) => {
    const [recommendationIds, setRecommendationIds] = useState([]);
    const [recommendationDetails, setRecommendationDetails] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { id } = useParams();
    const navigate = useNavigate();

    // Use a ref to keep track if the recommendations have been fetched
    const hasFetchedRecommendations = useRef(false);

    const fetchRecommendationIds = useCallback(async () => {
      if (recommendationIds.length > 0 || hasFetchedRecommendations.current)
        return;

      setLoading(true);
      setError(null);
      try {
        const response = await fetch(
          `${
            process.env.REACT_APP_API_URL
          }/api/user-recommendations?username=${encodeURIComponent(
            userData.username
          )}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            if (data.length === 0) {
              setError(
                "No recommendations found. Please generate recommendations first."
              );
            } else {
              setRecommendationIds(data.map((rec) => rec.recommendation_id));
            }
          } else {
            setError("Invalid data format: Expected an array");
          }
        } else {
          setError("Failed to fetch recommendation IDs.");
        }
      } catch (error) {
        setError("An error occurred while fetching recommendations.");
      } finally {
        setLoading(false);
        hasFetchedRecommendations.current = true;
      }
    }, [userData.username, recommendationIds]);

    useEffect(() => {
      fetchRecommendationIds();
    }, [fetchRecommendationIds]);

    const fetchRecommendationDetails = useCallback(
      async (recommendationId) => {
        if (recommendationDetails[recommendationId]) {
          onSelectPreviousRecommendation(
            recommendationDetails[recommendationId],
            recommendationId
          );
          return;
        }

        setLoading(true);
        setError(null);
        try {
          const response = await fetch(
            `${process.env.REACT_APP_API_URL}/api/recommendation/${recommendationId}`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
                "Content-Type": "application/json",
              },
            }
          );
          if (response.ok) {
            const data = await response.json();
            const reversedRecommendations = (data.recommendations || []).reverse();
            setRecommendationDetails((prev) => ({
              ...prev,
              [recommendationId]: reversedRecommendations,
            }));
            onSelectPreviousRecommendation(
              data.recommendations || [],
              recommendationId
            );
          } else {
            setError("Failed to fetch recommendation details.");
          }
        } catch (error) {
          setError("An error occurred while fetching recommendation details.");
        } finally {
          setLoading(false);
        }
      },
      [onSelectPreviousRecommendation, recommendationDetails]
    );

    useEffect(() => {
      if (id && !recommendationDetails[id]) {
        fetchRecommendationDetails(id);
      }
    }, [id, fetchRecommendationDetails, recommendationDetails]);

    const timeAgo = useMemo(
      () => (date) => formatDistanceToNow(new Date(date), { addSuffix: true }),
      []
    );

    return (
      <div className="reco-container">
        <button
          className="go-back-button"
          onClick={() => navigate("/recommender")}
        >
          <span className="back-arrow">{"< "}</span>Go back
        </button>
        <br></br>

        <h2>Previous Recommendations</h2>

        {/* <br></br> */}
        {loading && <p>Loading...</p>}
        {error ? (
          <p className="error-message">Error: {error}</p>
        ) : (
          recommendationIds.length > 0 && (
            <ul className="recommendation-ids">
              {recommendationIds.map((id, index) => (
                <li key={index}>
                  <button onClick={() => fetchRecommendationDetails(id)}>
                    {id}
                  </button>
                </li>
              ))}
            </ul>
          )
        )}
        {!loading && recommendationIds.length === 0 && !error && (
          <p>No recommendations available. Please generate some first.</p>
        )}
      </div>
    );
  }
);

export default PreviousRecommendations;
