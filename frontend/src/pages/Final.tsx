import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/layout/Header";
import ResultsTable from "../components/Table";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorPopup from "../components/ErrorPopup";

function Final() {
  const queryParams = new URLSearchParams(window.location.search);
  const [agilityID, setAgilityID] = useState("");
  const [jumpingID, setJumpingID] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getIds();
  }, []);

  const getIds = () => {
    setAgilityID(queryParams.get("agility") || "");
    setJumpingID(queryParams.get("jumping") || "");
  };

  const fetchFinal = async () => {
    if (!agilityID || !jumpingID) {
      console.warn("Missing agility or jumping IDs");
      return null;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/final?agility=${agilityID}&jumping=${jumpingID}`,
      );
      if (!response.ok) throw new Error("Failed to fetch final data");
      const data = await response.json();
      console.log("Final data:", data);
      return data;
    } catch (error) {
      console.error("Error fetching final data:", error);
    } finally {
      setLoading(false);
    }

    return null;
  };

  return (
    <>
      <Header />
      {loading && <LoadingSpinner />}
      {error && <ErrorPopup message={error} onClose={() => setError(null)} />}
      <div className="main-data-box">
        <p>Hello from the '/Final' page</p>

        <p>Agility ID: {agilityID}</p>
        <p>Jumping ID: {jumpingID}</p>

        <div className="secondary-data-box">
          <ResultsTable />
        </div>
      </div>
    </>
  );
}

export default Final;
