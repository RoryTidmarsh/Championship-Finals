import { useEffect, useState } from "react";

function Selection() {
  // Form for selecing the show and the height

  const shows = ["Show 1", "Show 2", "Show 3"];
  const heights = ["Height 1", "Height 2", "Height 3"];

  const [selectedShow, setSelectedShow] = useState("Select Show");
  const [selectedHeight, setSelectedHeight] = useState("Select height");

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
        >
          {selectedShow}
        </button>
        <ul className="dropdown-menu" aria-labelledby="showDropdown">
          {shows.map((show) => (
            <li key={show}>
              <a
                className="dropdown-item"
                href="#"
                onClick={(event) => {
                  event.preventDefault();
                  setSelectedShow(show);
                }}
              >
                {show}
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
    </>
  );
}

export default Selection;
