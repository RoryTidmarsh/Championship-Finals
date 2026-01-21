import Header from "../components/layout/Header";

function Home() {
  return (
    <>
      <Header />
      <div
        className="main-data-box d-flex align-items-center justify-content-center gap-3 flex-column"
        style={{
          marginTop: "2.5rem",
          backgroundColor: "rgba(70, 70, 70, 0.65)",
          width: "80%",
          padding: "2rem",
          borderRadius: "15px",
          position: "relative", //
          left: "50%", // Center horizontally
          transform: "translateX(-50%)", // Center horizontally
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
          textAlign: "center",
        }}
      >
        <p>Hello from the '/Final' page</p>
      </div>
    </>
  );
}

export default Home;
