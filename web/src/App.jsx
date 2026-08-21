import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";
import AnalyticsPage from "./pages/AnalyticsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import PortfolioDetailPage from "./pages/PortfolioDetailPage";
import PortfoliosPage from "./pages/PortfoliosPage";
import RegisterPage from "./pages/RegisterPage";
import MarketDashboardPage from "./pages/MarketDashboardPage";
import WatchlistPage from "./pages/WatchlistPage";
import StockAnalyzerPage from "./pages/StockAnalyzerPage";
import PortfolioLivePage from "./pages/PortfolioLivePage";
import RiskAnalyticsPage from "./pages/RiskAnalyticsPage";
import MTFDashboardPage from "./pages/MTFDashboardPage";
import MTFConcentrationPage from "./pages/MTFConcentrationPage";
import EnterpriseRMSPage from "./pages/EnterpriseRMSPage";
import EnterpriseRMSHistoryPage from "./pages/EnterpriseRMSHistoryPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/portfolios" element={<PortfoliosPage />} />
          <Route
            path="/portfolios/:portfolioId"
            element={<PortfolioDetailPage />}
          />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/market" element={<MarketDashboardPage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route
            path="/stock-analyzer"
            element={<StockAnalyzerPage />}
          />
          <Route
            path="/portfolio-live"
            element={<PortfolioLivePage />}
          />
          <Route
            path="/risk-analytics"
            element={<RiskAnalyticsPage />}
          />
          <Route
            path="/mtf-dashboard"
            element={<MTFDashboardPage />}
          />

          {/* MTF Concentration Risk */}
          <Route
            path="/mtf-concentration"
            element={<MTFConcentrationPage />}
          />

          {/* Historical Risk Analytics */}
          <Route
            path="/enterprise-rms/history"
            element={<EnterpriseRMSHistoryPage />}
          />

          {/* Enterprise RMS */}
          <Route
            path="/enterprise-rms"
            element={<EnterpriseRMSPage />}
          />
        </Route>
      </Route>

      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}