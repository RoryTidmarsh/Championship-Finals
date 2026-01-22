import { useState, useEffect } from "react";
import Header from "../components/layout/Header";
import Selection from "../components/Selection";
import UrlDropdown from "../components/URLdropdown";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorPopup from "../components/ErrorPopup";

function Home() {
  const [selectedShow, setSelectedShow] = useState("Select Show");
  const [selectedHeight, setSelectedHeight] = useState("Select height");
  const [selectedDate, setSelectedDate] = useState("");
  const [shows, setShows] = useState<Array<{ show: string; date: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const showSelected = false;

  const [agilityUrl, setAgilityUrl] = useState("");
  const [jumpingUrl, setJumpingUrl] = useState("");

  useEffect(() => {
    fetchShows();
  }, []);

  const fetchShows = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        import.meta.env.VITE_API_URL + "/near-shows",
      );
      const data = await response.json();
      setShows(data.shows);
    } catch (error) {
      console.error("Error fetching shows:", error);
    } finally {
      setLoading(false);
    }
  };
  const handleSubmit = async () => {
    setError(null);
    setLoading(true);

    // Prep for 2 types of processing
    const hasUrls = agilityUrl && jumpingUrl;
    const hasSelection =
      selectedShow !== "Select Show" && selectedHeight !== "Select height";

    // Error parsing
    if (!hasUrls && !hasSelection) {
      setError("Either select show/height or input class urls");
      return;
    }

    let endpoint = hasUrls ? "/lookup-ids-url" : "/lookup-ids";
    let requestBody = hasUrls
      ? { agilityUrl: agilityUrl, jumpingUrl: jumpingUrl }
      : { show: selectedShow, height: selectedHeight };

    try {
      const response = await fetch(import.meta.env.VITE_API_URL + endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage =
          errorData.detail ||
          "Failed to fetch IDs. Please check your selection and try again.";
        setError(errorMessage);
        setLoading(false);
        return;
      }

      const data = await response.json();
      console.log(`AgilityID: ${data.agilityID}, JumpingID: ${data.jumpingID}`);

      // Use response data directly for navigation (don't wait for state)
      const params = new URLSearchParams({
        agility: data.agilityID,
        jumping: data.jumpingID,
      });
      window.location.href = `/final?${params.toString()}`;
    } catch (error) {
      console.error("Error fetching IDs:", error);
      setError("Failed to connect to the server. Please try again.");
      setLoading(false);
    }
  };

  const handleShowSelect = (show: string, date: string) => {
    setSelectedShow(show);
    setSelectedDate(date);
  };

  const handleHeightSelect = (height: string) => {
    setSelectedHeight(height);
  };

  return (
    <>
      <Header />
      {loading && <LoadingSpinner />}
      {error && <ErrorPopup message={error} onClose={() => setError(null)} />}
      <div className="main-data-box">
        <Selection
          shows={shows}
          loading={loading}
          selectedShow={selectedShow}
          selectedHeight={selectedHeight}
          onShowSelect={handleShowSelect}
          onHeightSelect={handleHeightSelect}
        />
        {showSelected && (
          <div className="secondary-data-box">
            <p>Selected Show: {selectedShow}</p>
            <p>Selected Date: {selectedDate}</p>
            <p>Selected Height: {selectedHeight}</p>
          </div>
        )}
        <UrlDropdown
          agilityUrl={agilityUrl}
          jumpingUrl={jumpingUrl}
          onAgilityUrlChange={setAgilityUrl}
          onJumpingUrlChange={setJumpingUrl}
        />
        <button
          onClick={handleSubmit}
          style={{ borderRadius: "10px" }}
          disabled={
            ((selectedShow === "Select Show" ||
              selectedHeight === "Select height") &&
              !agilityUrl) ||
            !jumpingUrl ||
            loading
          }
        >
          Submit
        </button>
      </div>
    </>
  );
}

export default Home;
