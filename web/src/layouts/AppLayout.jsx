import {
  AccountBalance,
  AccountBalanceWallet,
  AdminPanelSettings,
  Analytics,
  Assessment,
  Brightness4,
  Brightness7,
  Dashboard,
  Logout,
  Menu as MenuIcon,
  Search,
  Security,
  ShowChart,
  Star,
  TrendingUp,
} from "@mui/icons-material";
import {
  AppBar,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Toolbar,
  Typography,
} from "@mui/material";
import { useState } from "react";
import {
  Link,
  Outlet,
  useLocation,
} from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useThemeMode } from "../contexts/ThemeModeContext";

const drawerWidth = 250;

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: <Dashboard />,
  },
  {
    label: "Portfolios",
    path: "/portfolios",
    icon: <AccountBalanceWallet />,
  },
  {
    label: "Analytics",
    path: "/analytics",
    icon: <Analytics />,
  },
  {
    label: "Live Market",
    path: "/market",
    icon: <ShowChart />,
  },
  {
    label: "Watchlist",
    path: "/watchlist",
    icon: <Star />,
  },
  {
    label: "Stock Analyzer",
    path: "/stock-analyzer",
    icon: <Search />,
  },
  {
    label: "Portfolio Live",
    path: "/portfolio-live",
    icon: <TrendingUp />,
  },
  {
    label: "Risk Analytics",
    path: "/risk-analytics",
    icon: <Security />,
  },
  {
    label: "MTF Dashboard",
    path: "/mtf-dashboard",
    icon: <AccountBalance />,
  },
  {
  label: "MTF Concentration",
  path: "/mtf-concentration",
  icon: <Assessment />,
  },
  {
  label: "Historical Risk Analytics",
  path: "/enterprise-rms/history",
  icon: <Assessment />,
  },
  {
    label: "Enterprise RMS",
    path: "/enterprise-rms",
    icon: <AdminPanelSettings />,
  },
];

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();
  const {
    isDarkMode,
    mode,
    toggleTheme,
  } = useThemeMode();

  const drawer = (
    <Box>
      <Toolbar>
        <Typography
          fontWeight={800}
          lineHeight={1.15}
        >
          Finance
          <br />
          Utility Suite
        </Typography>
      </Toolbar>

      <Divider />

      <List>
        {navigation.map((item) => (
          <ListItemButton
            component={Link}
            key={item.path}
            selected={location.pathname.startsWith(
              item.path,
            )}
            to={item.path}
            onClick={() => setMobileOpen(false)}
          >
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
      }}
    >
      <AppBar
        position="fixed"
        color="default"
        sx={{
          ml: { md: `${drawerWidth}px` },
          width: {
            md: `calc(100% - ${drawerWidth}px)`,
          },
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            onClick={() => setMobileOpen(true)}
            sx={{
              mr: 2,
              display: { md: "none" },
            }}
          >
            <MenuIcon />
          </IconButton>

          <Typography
            sx={{ flexGrow: 1 }}
            fontWeight={700}
          >
            Welcome, {user?.name}
          </Typography>

          <Tooltip
            title={
              isDarkMode
                ? "Switch to light theme"
                : "Switch to dark theme"
            }
          >
            <IconButton
              onClick={toggleTheme}
              aria-label={`Switch to ${
                isDarkMode ? "light" : "dark"
              } theme`}
              sx={{ mr: 1 }}
            >
              {isDarkMode ? (
                <Brightness7 />
              ) : (
                <Brightness4 />
              )}
            </IconButton>
          </Tooltip>

          <Typography
            variant="body2"
            sx={{
              mr: 2,
              display: {
                xs: "none",
                sm: "block",
              },
              textTransform: "capitalize",
            }}
          >
            {mode} mode
          </Typography>

          <Button
            color="inherit"
            startIcon={<Logout />}
            onClick={logout}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { md: drawerWidth },
          flexShrink: { md: 0 },
        }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: {
              xs: "block",
              md: "none",
            },
            "& .MuiDrawer-paper": {
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        <Drawer
          variant="permanent"
          sx={{
            display: {
              xs: "none",
              md: "block",
            },
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: {
            md: `calc(100% - ${drawerWidth}px)`,
          },
          p: 3,
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
