import { Navigate, useOutlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { NavBar } from "./NavBar";

export const HomeLayout = () => {
  const { user } = useAuth();
  const outlet = useOutlet();

  if (user) {
    return <Navigate to="/simulador" replace />;
  }

  return (
    <>
      <NavBar />
      {outlet}
    </>
  );
};

export default HomeLayout;
