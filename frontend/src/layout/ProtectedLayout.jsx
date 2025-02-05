import { Navigate, Outlet } from "react-router-dom";
import { getCurrentUser } from "../firebase/authFirebase";

const ProtectedLayout = () => {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedLayout;
