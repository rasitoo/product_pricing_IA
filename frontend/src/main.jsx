import React from "react";
import { createRoot } from "react-dom/client";

import { CarouselPage } from "./pages/CarouselPage.jsx";
import { ReviewPage } from "./pages/ReviewPage.jsx";

function App() {
  const [path, setPath] = React.useState(window.location.pathname);

  React.useEffect(() => {
    if (path === "/") {
      window.history.replaceState(null, "", "/carousel");
      setPath("/carousel");
    }
  }, [path]);

  if (path === "/review") return <ReviewPage />;
  return <CarouselPage />;
}

createRoot(document.getElementById("root")).render(<App />);
