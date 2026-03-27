import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// Global styles
document.body.style.margin = "0";
document.body.style.padding = "0";
document.body.style.overflow = "hidden";
document.body.style.background = "#1a1a2e";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
