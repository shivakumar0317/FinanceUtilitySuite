import {CircularProgress,Stack} from "@mui/material";
import {Navigate,Outlet} from "react-router-dom";
import {useAuth} from "../contexts/AuthContext";
export default function ProtectedRoute(){const {isAuthenticated,loading}=useAuth();if(loading)return <Stack alignItems="center" justifyContent="center" minHeight="100vh"><CircularProgress/></Stack>;return isAuthenticated?<Outlet/>:<Navigate to="/login" replace/>;}
