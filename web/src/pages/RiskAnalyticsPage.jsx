import { Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import RiskDrawdownChart from "../components/RiskDrawdownChart";
import RiskPerformanceChart from "../components/RiskPerformanceChart";
import RiskSummaryCards from "../components/RiskSummaryCards";
import SectorExposureChart from "../components/SectorExposureChart";
import TopRiskHoldingsTable from "../components/TopRiskHoldingsTable";
import api from "../services/api";

const periodOptions = [
  { value: "6mo", label: "6 Months" },
  { value: "1y", label: "1 Year" },
  { value: "2y", label: "2 Years" },
  { value: "5y", label: "5 Years" },
];

export default function RiskAnalyticsPage() {
  const [period, setPeriod] = useState("1y");

  const risk = useQuery({
    queryKey: ["risk-analytics", period],
    queryFn: async () =>
      (
        await api.get(
          "/api/risk-analytics/dashboard",
          {
            params: { period },
          },
        )
      ).data,
    refetchOnWindowFocus: false,
  });

  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ sm: "center" }}
        spacing={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Risk Analytics
          </Typography>
          <Typography color="text.secondary">
            Portfolio risk compared with NIFTY 50.
          </Typography>
        </Box>

        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1}
        >
          <TextField
            select
            label="Analysis Period"
            value={period}
            onChange={(event) =>
              setPeriod(event.target.value)
            }
            sx={{ minWidth: 150 }}
          >
            {periodOptions.map((option) => (
              <MenuItem
                key={option.value}
                value={option.value}
              >
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => risk.refetch()}
            disabled={risk.isFetching}
          >
            Refresh
          </Button>
        </Stack>
      </Stack>

      {risk.isLoading && (
        <Stack alignItems="center" py={8}>
          <CircularProgress />
        </Stack>
      )}

      {risk.isError && (
        <Alert severity="error">
          {risk.error.response?.data?.detail ||
            "Unable to load risk analytics. Upload a portfolio in Portfolio Live first."}
        </Alert>
      )}

      {risk.data && (
        <>
          <RiskSummaryCards
            summary={risk.data.summary}
          />

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <RiskPerformanceChart
                data={risk.data.performance}
              />
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <RiskDrawdownChart
                data={risk.data.drawdown}
              />
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <SectorExposureChart
                data={risk.data.sector_exposure}
              />
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <Stack spacing={1}>
                <Alert severity="info">
                  Benchmark:{" "}
                  {risk.data.summary.benchmark_symbol}
                  {" · "}
                  Period:{" "}
                  {risk.data.summary.analysis_period}
                </Alert>

                <Alert
                  severity={
                    risk.data.summary.risk_level === "High"
                      ? "error"
                      : risk.data.summary.risk_level ===
                          "Moderate"
                        ? "warning"
                        : "success"
                  }
                >
                  Overall Portfolio Risk:{" "}
                  {risk.data.summary.risk_level}
                </Alert>
              </Stack>
            </Grid>
          </Grid>

          <TopRiskHoldingsTable
            rows={risk.data.top_risk_holdings}
          />
        </>
      )}
    </Stack>
  );
}
