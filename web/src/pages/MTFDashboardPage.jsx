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
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import MTFClientRiskTable from "../components/MTFClientRiskTable";
import MTFDataTables from "../components/MTFDataTables";
import MTFMarginDistributionChart from "../components/MTFMarginDistributionChart";
import MTFSummaryCards from "../components/MTFSummaryCards";
import MTFSymbolExposureChart from "../components/MTFSymbolExposureChart";
import MTFUploadCard from "../components/MTFUploadCard";
import api from "../services/api";

export default function MTFDashboardPage() {
  const [dashboardData, setDashboardData] =
    useState(null);

  const upload = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append("file", file);

      return (
        await api.post(
          "/api/mtf/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          },
        )
      ).data;
    },
    onSuccess: (data) => {
      setDashboardData(data);
    },
  });

  const dashboard = useQuery({
    queryKey: ["mtf-dashboard"],
    enabled: false,
    queryFn: async () =>
      (await api.get("/api/mtf/dashboard")).data,
  });

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

      <MTFUploadCard
        onUpload={(file) => upload.mutate(file)}
        uploading={upload.isPending}
        error={
          upload.error?.response?.data?.detail ||
          (upload.isError
            ? "Unable to upload MTF file."
            : "")
        }
      />

      {(upload.isPending ||
        dashboard.isFetching) && (
        <Stack alignItems="center" py={5}>
          <CircularProgress />
        </Stack>
      )}

      {dashboard.isError && (
        <Alert severity="error">
          {dashboard.error.response?.data?.detail ||
            "Unable to refresh MTF dashboard."}
        </Alert>
      )}

      {dashboardData && (
        <>
          <Alert
            severity={riskSeverity(
              dashboardData.summary.risk_level,
            )}
          >
            Overall MTF Risk Level:{" "}
            {dashboardData.summary.risk_level}
          </Alert>

          <MTFSummaryCards
            summary={dashboardData.summary}
          />

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
                data={dashboardData.symbol_exposure}
              />
            </Grid>
          </Grid>

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

          <MTFClientRiskTable
            rows={dashboardData.client_risk}
          />
        </>
      )}
    </Stack>
  );
}
