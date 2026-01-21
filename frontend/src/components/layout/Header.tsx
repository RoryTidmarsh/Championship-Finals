function Header() {
  return (
    <>
      <div
        className="d-flex align-items-center justify-content-center gap-3"
        style={{
          top: 10,
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          padding: "1rem 1.5rem",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          position: "relative",
          width: "fit-content",
          borderRadius: "15px",
          left: "50%",
          transform: "translateX(-50%)",
        }}
      >
        <img
          src="/champFinals.png"
          alt="Logo"
          className="Logo"
          style={{ height: "85px", width: "85px", cursor: "pointer" }}
          onClick={() => (window.location.href = "/")}
        ></img>
        <h1
          className="mt-0 text-green fw-bold"
          style={{ fontSize: "2.25rem", color: "#37c15e" }}
        >
          Champ Finals <strong>Live</strong>
        </h1>
      </div>
    </>
  );
}

export default Header;
