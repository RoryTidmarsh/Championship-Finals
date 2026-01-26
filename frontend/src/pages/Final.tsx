import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/layout/Header";
import ResultsTable from "../components/Table";

function Final() {
  const queryParams = new URLSearchParams(window.location.search);
  const [agilityID, setAgilityID] = useState("");
  const [jumpingID, setJumpingID] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getIds();
  }, []);

  const getIds = () => {
    setAgilityID(queryParams.get("agility") || "");
    setJumpingID(queryParams.get("jumping") || "");
  };

  const fetchFinal = async () => {
    setLoading(true);
    try {
      const response = await fetch(import.meta.env.VITE_API_URL + "/final");
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
