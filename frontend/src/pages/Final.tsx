import { useEffect, useState } from "react";
import Header from "../components/layout/Header";
import ResultsTable from "../components/Table";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorPopup from "../components/ErrorPopup";

function Final() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [finalData, setFinalData] = useState<any>(null);

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

        <div className="secondary-data-box">
          {finalData && (
            <ResultsTable
              loading={loading}
              data={finalData.final || { rows: [] }}
              columns={[]}
              positionBased={true}
            />
          )}
        </div>
      </div>
    </>
  );
}

export default Final;
