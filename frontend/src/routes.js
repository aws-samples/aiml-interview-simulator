import {
  defer,
  Route,
  createBrowserRouter,
  createRoutesFromElements,
} from "react-router-dom";
import AuthLayout from "./components/AuthLayout";
import { HomeLayout } from "./components/HomeLayout";
import ProtectedLayout from "./components/ProtectedLayout";
import LogIn from "./pages/LogIn";
import Simulador from "./pages/Simulador";

// idealmente chamada para API
const getUserData = () =>
  new Promise((resolve) =>
    setTimeout(() => {
      const user = window.localStorage.getItem("user");
      resolve(user);
    }, 3000)
  );

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route
      element={<AuthLayout />}
      loader={() => defer({ userPromise: getUserData() })}
    >
      <Route element={<HomeLayout />}>
        <Route path="/" element={<LogIn />} />
      </Route>
      <Route element={<ProtectedLayout />}>
        <Route path="/simulador" element={<Simulador />} />
      </Route>
    </Route>
  )
);

export default router;
