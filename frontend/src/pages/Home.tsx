import { useState, useEffect } from "react";
import Header from "../components/layout/Header";
import Selection from "../components/Selection";
import UrlDropdown from "../components/URLdropdown";

function Home() {
  const [selectedShow, setSelectedShow] = useState("Select Show");
  const [selectedHeight, setSelectedHeight] = useState("Select height");
  const [selectedDate, setSelectedDate] = useState("");
  const [shows, setShows] = useState<Array<{ show: string; date: string }>>([]);
  const [loading, setLoading] = useState(false);

  const showSelected = false;

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

  const fetchIds = async () => {
    setLoading(true);

    try {
      const response = await fetch(
        import.meta.env.VITE_API_URL + "/lookup-ids",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json", // Let backend know a json request
          },
          body: JSON.stringify({
            show: selectedShow,
            height: selectedHeight,
          }),
        },
      );
      const data = await response.json();
      console.log(`AgilityID: ${data.agilityID}, JumpingID: ${data.jumpingID}`);
    } catch (error) {
      console.error("Error fetching IDs:", error);
    } finally {
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
        <UrlDropdown />
        <button
          onClick={fetchIds}
          style={{ borderRadius: "10px" }}
          disabled={
            selectedShow === "Select Show" ||
            selectedHeight === "Select height" ||
            loading
          }
        >
          Go to Final Page
        </button>
      </div>
    </>
  );
}

export default Home;
