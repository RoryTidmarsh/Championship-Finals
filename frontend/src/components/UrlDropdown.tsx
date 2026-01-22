import { useState } from "react";
interface UrlDropdownProps {
  agilityUrl: string;
  jumpingUrl: string;
  onAgilityUrlChange: (url: string) => void;
  onJumpingUrlChange: (url: string) => void;
}

function UrlDropdown({
  agilityUrl,
  jumpingUrl,
  onAgilityUrlChange,
  onJumpingUrlChange,
}: UrlDropdownProps) {
  const [btnState, setButtonState] = useState(false);
  // const [agilityUrl, setAgilityUrl] = useState("");
  // const [jumpingUrl, setJumpingUrl] = useState("");

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
            // className="d-flex align-items-center gap-2 justify-content-center flex-column slide-down"
            // style={{
            //   backgroundColor: "rgba(45, 45, 45)",
            //   width: "100%",
            //   padding: "0.75rem",
            //   marginTop: "0.5rem",
            //   borderRadius: "11px",
            //   border: "1px solid #000000",
            //   color: "white",
            // }}
            className="secondary-data-box"
            style={{ marginTop: "0.5rem", color: "white" }}
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
                  onChange={(e) => onAgilityUrlChange(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <label>Jumping Class URL</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. www.agilityplaza.co.uk/agilityClass/9876543210/results"
                  value={jumpingUrl}
                  onChange={(e) => onJumpingUrlChange(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default UrlDropdown;
