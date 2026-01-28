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

  const formatDate = (date: string) => {
    // Date comes in at YYYY-MM-DD
    // Convert to DD-MMM-YY
    const dateObj = new Date(date);
    const day = String(dateObj.getDate()).padStart(2, "0");
    const month = dateObj.toLocaleString("en-US", { month: "short" });
    const year = String(dateObj.getFullYear()).slice(-2);
    return `${day}-${month}-${year}`;
  };

  return (
    <>
      <div 
        className="secondary-data-box secondary-data-box--row" 
        style={{ 
          flexWrap: "wrap",
          gap: "0.75rem",
          alignItems: "center"
        }}
      >
        <p className="mb-0">Show:</p>
        <button
          className="btn btn-secondary dropdown-toggle"
          type="button"
          id="showDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          style={{ minWidth: "150px" }}
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
                {show.show} ({formatDate(show.date)})
              </a>
            </li>
          ))}
        </ul>

        <p className="mb-0">
          Height:
        </p>
        <button
          className="btn btn-secondary dropdown-toggle"
          type="button"
          id="heightDropdown"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          style={{ minWidth: "120px" }}
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
