interface SelectionProps {
  shows: Array<{ show: string; date: string }>;
  loading: boolean;
  selectedShow: string;
  selectedHeight: string;
  onShowSelect: (show: string, date: string) => void;
  onHeightSelect: (height: string) => void;
}

function Selection({
  shows,
  loading,
  selectedShow,
  selectedHeight,
  onShowSelect,
  onHeightSelect,
}: SelectionProps) {
  const heights = ["Lge", "Int", "Med", "Sml"];

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
          // disabled={loading}
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
                  onShowSelect(show.show, show.date);
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
                  onHeightSelect(height);
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
