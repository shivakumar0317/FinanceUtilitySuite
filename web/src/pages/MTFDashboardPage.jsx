import { Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Grid,
  Stack,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import MTFClientRiskTable from "../components/MTFClientRiskTable";
import MTFDataTables from "../components/MTFDataTables";
import MTFMarginDistributionChart from "../components/MTFMarginDistributionChart";
import MTFSummaryCards from "../components/MTFSummaryCards";
import MTFSymbolExposureChart from "../components/MTFSymbolExposureChart";
import api from "../services/api";

export default function MTFDashboardPage() {
  const [dashboardData, setDashboardData] = useState(null);

  const dashboard = useQuery({
    queryKey: ["mtf-dashboard"],
    enabled: true,
    retry: false,
    queryFn: async () =>
      (await api.get("/api/mtf/dashboard")).data,
  });

  useEffect(() => {
    if (dashboard.data) {
      setDashboardData(dashboard.data);
    }
  }, [dashboard.data]);

  const refreshDashboard = async () => {
    const result = await dashboard.refetch();

    if (result.data) {
      setDashboardData(result.data);
    }
  };

  const riskSeverity = (riskLevel) => {
    if (riskLevel === "High") {
      return "error";
    }

    if (riskLevel === "Moderate") {
      return "warning";
    }

    return "success";
  };

  return (
    <Stack spacing={3}>
      {/* Page Header */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ sm: "center" }}
        spacing={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            MTF Dashboard
          </Typography>

          <Typography color="text.secondary">
            Margin trading facility exposure and risk analysis.
          </Typography>
        </Box>

        {dashboardData && (
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshDashboard}
            disabled={dashboard.isFetching}
          >
            Refresh
          </Button>
        )}
      </Stack>

      {/* Dashboard Loading */}
      {dashboard.isFetching && !dashboardData && (
        <Stack alignItems="center" py={8}>
          <CircularProgress />
        </Stack>
      )}

      {/* Dashboard Error */}
      {dashboard.isError && (
        <Alert severity="error">
          {dashboard.error?.response?.data?.detail ||
            "Unable to refresh MTF dashboard."}
        </Alert>
      )}

      {/* Dashboard Data */}
      {dashboardData && (
        <>
          {/* Overall Risk */}
          <Alert
            severity={riskSeverity(
              dashboardData.summary.risk_level,
            )}
          >
            Overall MTF Risk Level:{" "}
            {dashboardData.summary.risk_level}
          </Alert>

          {/* Summary Cards */}
          <MTFSummaryCards
            summary={dashboardData.summary}
          />

          {/* Charts */}
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <MTFMarginDistributionChart
                data={
                  dashboardData.margin_distribution
                }
              />
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <MTFSymbolExposureChart
                data={
                  dashboardData.cap_net_value_distribution
                }
              />
            </Grid>
          </Grid>

          {/* Data Tables */}
          <MTFDataTables
            topMarginClients={
              dashboardData.top_margin_clients
            }
            topMarginSymbols={
              dashboardData.top_margin_symbols
            }
            topMtmGainers={
              dashboardData.top_mtm_gainers
            }
            topMtmLosers={
              dashboardData.top_mtm_losers
            }
          />

          {/* Client Risk */}
          <MTFClientRiskTable
            rows={dashboardData.client_risk}
          />
        </>
      )}
    </Stack>
  );
}