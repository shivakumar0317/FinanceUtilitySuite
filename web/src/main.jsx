import {CssBaseline,ThemeProvider,createTheme} from "@mui/material";
import {QueryClient,QueryClientProvider} from "@tanstack/react-query";
import React from "react";import ReactDOM from "react-dom/client";import {BrowserRouter} from "react-router-dom";
import App from "./App";import {AuthProvider} from "./contexts/AuthContext";
const queryClient=new QueryClient({defaultOptions:{queries:{retry:1,refetchOnWindowFocus:false}}});
const theme=createTheme({palette:{mode:"dark",primary:{main:"#3b82f6"},background:{default:"#0b1220",paper:"#111827"}},shape:{borderRadius:12},typography:{fontFamily:'"Segoe UI", Inter, Arial, sans-serif'}});
ReactDOM.createRoot(document.getElementById("root")).render(<React.StrictMode><QueryClientProvider client={queryClient}><ThemeProvider theme={theme}><CssBaseline/><BrowserRouter><AuthProvider><App/></AuthProvider></BrowserRouter></ThemeProvider></QueryClientProvider></React.StrictMode>);
