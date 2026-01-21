import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useEffect } from "react";

// Pages
import Home from "./pages/Home";
import Final from "./pages/Final";
import ApiTest from "./components/ApiTest";

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
          <Route path="/test" element={<ApiTest />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
