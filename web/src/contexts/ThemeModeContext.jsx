import {
  createContext,
  useContext,
  useMemo,
  useState,
} from "react";
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
} from "@mui/material";

const ThemeModeContext = createContext(null);

const STORAGE_KEY = "fus_theme_mode";

const buildTheme = (mode) =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: mode === "dark" ? "#60a5fa" : "#2563eb",
      },
      secondary: {
        main: mode === "dark" ? "#34d399" : "#059669",
      },
      background: {
        default: mode === "dark" ? "#0b1220" : "#f5f7fb",
        paper: mode === "dark" ? "#111827" : "#ffffff",
      },
    },
    shape: {
      borderRadius: 12,
    },
    typography: {
      fontFamily: '"Segoe UI", Inter, Arial, sans-serif',
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: "none",
            borderBottom:
              mode === "dark"
                ? "1px solid rgba(255,255,255,0.08)"
                : "1px solid rgba(15,23,42,0.10)",
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            border:
              mode === "dark"
                ? "1px solid rgba(255,255,255,0.06)"
                : "1px solid rgba(15,23,42,0.08)",
            boxShadow:
              mode === "dark"
                ? "0 8px 24px rgba(0,0,0,0.24)"
                : "0 8px 24px rgba(15,23,42,0.08)",
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundImage: "none",
            borderRight:
              mode === "dark"
                ? "1px solid rgba(255,255,255,0.08)"
                : "1px solid rgba(15,23,42,0.10)",
          },
        },
      },
    },
  });

export function ThemeModeProvider({ children }) {
  const [mode, setMode] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved === "light" || saved === "dark") {
      return saved;
    }

    return "dark";
  });

  const toggleTheme = () => {
    setMode((currentMode) => {
      const nextMode =
        currentMode === "dark" ? "light" : "dark";

      localStorage.setItem(STORAGE_KEY, nextMode);
      return nextMode;
    });
  };

  const theme = useMemo(() => buildTheme(mode), [mode]);

  const value = useMemo(
    () => ({
      mode,
      toggleTheme,
      isDarkMode: mode === "dark",
    }),
    [mode],
  );

  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
}

export function useThemeMode() {
  const context = useContext(ThemeModeContext);

  if (!context) {
    throw new Error(
      "useThemeMode must be used inside ThemeModeProvider.",
    );
  }

  return context;
}
