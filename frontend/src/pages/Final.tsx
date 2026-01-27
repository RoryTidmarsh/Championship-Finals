import { useEffect, useState } from "react";
import Header from "../components/layout/Header";
import ResultsTable from "../components/Table";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorPopup from "../components/ErrorPopup";

function Final() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [finalData, setFinalData] = useState<any>(null);

  const [positionBased, setPositionBased] = useState(true);

  useEffect(() => {
    const fetchFinalData = async () => {
      const queryParams = new URLSearchParams(window.location.search);
      const agility = queryParams.get("agility");
      const jumping = queryParams.get("jumping");

      if (!agility || !jumping) {
        setError(
          "Either Agility or jumping ID are not provided in the URL params",
        );
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/final?agility=${agility}&jumping=${jumping}`,
        );
        if (!response.ok) throw new Error("Failed to fetch final data");
        const data = await response.json();
        console.log("Final API response:", data);
        setFinalData(data);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        console.error("Error fetching final data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchFinalData();
  }, []);

  return (
    <>
      <Header />
      {loading && <LoadingSpinner />}
      {error && <ErrorPopup message={error} onClose={() => setError(null)} />}
      <div className="main-data-box">
        <p>Hello from the '/Final' page</p>
        {finalData && (
          <>
            <p>Agility Status: {finalData.agilityStatus}</p>
            <p>Jumping Status: {finalData.jumpingStatus}</p>
          </>
        )}

        <div className="secondary-data-box">
          <div className="d-flex align-items-center gap-3">
            <p
              className="mb-0"
              style={{
                fontWeight: "600",
                fontSize: "1.1rem",
              }}
            >
              Combine by:{" "}
            </p>
            <div
              className="btn-group align-items-center justify-content-center"
              role="group"
            >
              <button
                onClick={() => setPositionBased(true)}
                style={{
                  backgroundColor: positionBased
                    ? "var(--primary-color)"
                    : "rgba(4, 64, 31, 0.8)",
                  borderRadius: "15px 0 0 15px",
                }}
                disabled={positionBased}
              >
                {"Position"}
              </button>
              <button
                onClick={() => setPositionBased(false)}
                style={{
                  backgroundColor: !positionBased
                    ? "var(--primary-color)"
                    : "rgba(4, 64, 31, 0.8)",
                  borderRadius: "0 15px 15px 0",
                }}
                disabled={!positionBased}
              >
                {"Faults & Time"}
              </button>
            </div>
          </div>
          {finalData && (
            <>
              <h3 className="text-white">
                Agility Winner: {finalData.agilityWinner}
              </h3>
              <h3 className="text-white">
                Jumping Winner: {finalData.jumpingWinner}
              </h3>
              <ResultsTable
                data={
                  finalData.finalResults
                    ? JSON.parse(finalData.finalResults)
                    : { rows: [] }
                }
                positionBased={positionBased}
                jumpingWinner={finalData.jumpingWinner}
                agilityWinner={finalData.agilityWinner}
              />
            </>
          )}
        </div>
      </div>
    </>
  );
}

export default Final;
