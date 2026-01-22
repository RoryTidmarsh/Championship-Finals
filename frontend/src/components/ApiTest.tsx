import { useState, useEffect } from "react";
const ApiUrl = import.meta.env.VITE_API_URL;

function ShowList() {
  const [shows, setShows] = useState<Array<{ show: string; date: string }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log("ShowList component loaded, fetching data...");

    const fetchShows = async () => {
      setLoading(true);

      try {
        const response = await fetch(ApiUrl + "/near-shows");
        const data = await response.json();

        console.log("Shows recived!", data.shows);
        setShows(data.shows);
      } catch (error) {
        console.error("Error fetching shows: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchShows();
  }, []);

  return (
    <>
      <div
        style={{
          backgroundColor: "white",
        }}
      >
        <h2>Shows:</h2>
        {loading && <p>loading...</p>}
        <ul>
          {shows.map((show) => (
            <li key={show.show}>
              <strong>{show.show}</strong> - {show.date}
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}

function ApiTest() {
  const [message, setMessage] = useState("");

  const fetchHealth = async () => {
    try {
      const url = ApiUrl + "/health";
      const response = await fetch(url);
      const data = await response.json();

      console.log("Data recived", data);
      setMessage(data.status);
    } catch (error) {
      console.log("Error:", error);
      setMessage("Error Fetching Data");
    }
  };

  return (
    <div>
      <h2>API Test</h2>
      <button onClick={fetchHealth}>Test API</button>
      <p className="text-warning">Status: {message}</p>
      <br></br>

      <ShowList />
    </div>
  );
}

export default ApiTest;
