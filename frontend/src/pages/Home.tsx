import Header from "../components/layout/Header";

function Home() {
  return (
    <>
      <Header />
      <p>Hello from the '/Home' page</p>
      <button onClick={() => (window.location.href = "/final")}>
        Go to Final Page
      </button>
    </>
  );
}

export default Home;
