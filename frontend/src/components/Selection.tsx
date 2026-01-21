import { useState, useEffect } from "react";

const ApiUrl = import.meta.env.VITE_API_URL;

function dropdownForm() {
  const [btnState, setButtonState] = useState(false);
  const [agilityUrl, setAgilityUrl] = useState("");
  const [jumpingUrl, setJumpingUrl] = useState("");

  return (
    <>
      <div
        className="dropdown"
        style={{
          width: "100%",
        }}
      >
        <button
          type="button"
          className="btn btn-secondary dropdown-toggle"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          data-bs-auto-close="outside"
          style={{
            width: "80%",
            boxShadow: "0 0 10px rgba(40, 40, 40, 0.2)",
          }}
          onClick={() => setButtonState(!btnState)}
        >
          Can't find the class you're looking for?
        </button>

        {btnState && (
          <div
            className="d-flex align-items-center gap-2 justify-content-center flex-column"
            style={{
              backgroundColor: "rgba(45, 45, 45, 0.65)",
              width: "100%",
              padding: "0.75rem",
              marginTop: "0.5rem",
              borderRadius: "11px",
              // left: "50%",
              // transform: "translateX(-50%)",
              color: "white",
            }}
          >
            <h4>Input the link to results below</h4>
            <div style={{ width: "100%", maxWidth: "600px" }}>
              <div className="mb-3">
                <label>Agility Class URL</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. www.agilityplaza.co.uk/agilityClass/0123456789/results"
                  value={agilityUrl}
                  onChange={(e) => setAgilityUrl(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <label>Jumping Class URL</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. www.agilityplaza.co.uk/agilityClass/9876543210/results"
                  style={{ fontStyle: "italic" }}
                  value={jumpingUrl}
                  onChange={(e) => setJumpingUrl(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

function Selection() {
  const [shows, setShows] = useState<Array<{ show: string; date: string }>>([]);
  // const [heights, setHeights] = useState(["Height 1", "Height 2", "Height 3"]);
  const heights = ["Lge", "Int", "Med", "Sml"];
  const [selectedShow, setSelectedShow] = useState("Select Show");
  const [selectedHeight, setSelectedHeight] = useState("Select height");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchShows();
  }, []);

  const fetchShows = async () => {
    setLoading(true);
    try {
      const response = await fetch(ApiUrl + "/near-shows");
      const data = await response.json();
      setShows(data.shows);
    } catch (error) {
      console.error("Error fetching shows:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div
        className="dropdown d-flex align-items-center gap-2 justify-content-center"
        style={{
          backgroundColor: "rgba(45, 45, 45, 0.65)",
          width: "80%",
          padding: "0.75rem",
          borderRadius: "11px",
        }}
      >
        <p className="mb-0">Show:</p>
        <button
          className="btn btn-secondary dropdown-toggle"
          type="button"
          id="showDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          disabled={loading}
        >
          {selectedShow}
        </button>
        <ul className="dropdown-menu" aria-labelledby="showDropdown">
          {loading && (
            <li>
              <span className="dropdown-item">Loading...</span>
            </li>
          )}
          {shows.map((show) => (
            <li key={show.show}>
              <a
                className="dropdown-item"
                href="#"
                onClick={(event) => {
                  event.preventDefault();
                  setSelectedShow(show.show);
                }}
              >
                {show.show} - {show.date}
              </a>
            </li>
          ))}
        </ul>

        <p className="mb-0" style={{ marginLeft: "2rem" }}>
          Height:
        </p>
        <button
          className="btn btn-secondary dropdown-toggle"
          type="button"
          id="heightDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          {selectedHeight}
        </button>
        <ul className="dropdown-menu" aria-labelledby="heightDropdown">
          {heights.map((height) => (
            <li key={height}>
              <a
                className="dropdown-item"
                href="#"
                onClick={(event) => {
                  event.preventDefault();
                  setSelectedHeight(height);
                }}
              >
                {height}
              </a>
            </li>
          ))}
        </ul>
      </div>
      <p>Selected Show: {selectedShow}</p>
      <p>Selected height: {selectedHeight}</p>

      {dropdownForm()}
    </>
  );
}

export default Selection;
