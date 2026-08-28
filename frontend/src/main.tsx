import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./global.css"; // Points to your global styling sheet

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
