import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useEffect } from "react";

// Pages
import Home from "./pages/Home";
import Final from "./pages/Final";

// Utilities
import { getRandomBackgroundImage } from "./components/layout/backgroundUtils";

import "./App.css";

function App() {
  useEffect(() => {
    getRandomBackgroundImage();
  }, []);
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/final" element={<Final />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
