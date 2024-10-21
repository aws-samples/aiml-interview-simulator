import { Fragment } from "react";
import router from "./routes";
import { RouterProvider } from "react-router-dom";

function App() {
  return (
    <Fragment>
      <RouterProvider router={router} />
    </Fragment>
  );
}

export default App;
